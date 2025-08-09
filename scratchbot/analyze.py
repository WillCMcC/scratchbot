import os
import json
import argparse
import subprocess
import re
import ast
from typing import List, Dict, Any, Optional

TS_PARSER = os.path.join(os.path.dirname(__file__), 'ts_parser.js')

try:
    _NODE_MODULES = subprocess.check_output([
        'node', '-p', "require('path').resolve(process.execPath, '..', '..', 'lib', 'node_modules')"
    ], text=True).strip()
except Exception:
    _NODE_MODULES = ''

SKIP_DIRS = {'node_modules', 'dist', 'build', '.git', '__pycache__'}

def non_blank_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())

def analyze_js_ts_file(path: str) -> Dict[str, Any]:
    try:
        env = os.environ.copy()
        if _NODE_MODULES:
            env['NODE_PATH'] = _NODE_MODULES
        out = subprocess.check_output(['node', TS_PARSER, path], text=True, env=env)
        data = json.loads(out)
        return data
    except Exception:
        return {'exports': {'functions': [], 'classes': [], 'interfaces': []}, 'lines': non_blank_lines(open(path).read()), 'routes': []}

class PyAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.classes = []
        self.routes = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        if not node.name.startswith('_'):
            params = []
            for arg in node.args.args:
                params.append(arg.arg)
            if node.args.vararg:
                params.append('*' + node.args.vararg.arg)
            for arg in node.args.kwonlyargs:
                params.append(arg.arg)
            if node.args.kwarg:
                params.append('**' + node.args.kwarg.arg)
            sig = f"({','.join(params)})"
            self.functions.append({'name': node.name, 'signature': sig})
        for dec in node.decorator_list:
            route = self._extract_route(dec)
            if route:
                self.routes.append(route)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        if not node.name.startswith('_'):
            self.classes.append(node.name)
        self.generic_visit(node)

    def _extract_route(self, dec: ast.AST) -> Optional[str]:
        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
            if dec.func.attr in {'get', 'post', 'put', 'delete', 'patch'} and dec.args:
                arg = dec.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    return arg.value
        return None

def analyze_py_file(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    tree = ast.parse(text)
    analyzer = PyAnalyzer()
    analyzer.visit(tree)
    return {'exports': {'functions': analyzer.functions, 'classes': analyzer.classes}, 'lines': non_blank_lines(text), 'routes': analyzer.routes}

def parse_package_lock(path: str) -> List[str]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        deps = []
        for name, info in data.get('dependencies', {}).items():
            if not info.get('dev'):  # skip dev deps
                deps.append(name)
        return deps
    except Exception:
        return []

def parse_pnpm_lock(path: str) -> List[str]:
    deps = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        in_deps = False
        for line in lines:
            if line.startswith('dependencies:'):
                in_deps = True
                continue
            if in_deps:
                if not line.startswith('  '):
                    break
                name = line.strip().split(':')[0]
                if name:
                    deps.append(name)
        return deps
    except Exception:
        return []

def parse_requirements(path: str) -> List[str]:
    deps = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                name = re.split(r'[<>=]', line)[0]
                if name:
                    deps.append(name)
    except Exception:
        pass
    return deps

def analyze_repo(root: str, baseline_path: Optional[str] = None) -> Dict[str, Any]:
    js_results = []
    py_results = []
    missing_docs = set()
    dir_info: Dict[str, Dict[str, Any]] = {}
    snapshot_functions: Dict[str, Dict[str, str]] = {}
    snapshot_routes: Dict[str, List[str]] = {}

    root = os.path.abspath(root)

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        has_readme = any(name.lower() in ('readme.md', 'index.md') for name in filenames)
        dir_info[dirpath] = {'lines': 0, 'has_readme': has_readme}

        for filename in filenames:
            if filename.startswith('_'):
                continue
            path = os.path.join(dirpath, filename)
            relpath = os.path.relpath(path, root)
            if filename.endswith(('.ts', '.js')) and not filename.endswith('.d.ts'):
                data = analyze_js_ts_file(path)
                data['path'] = relpath
                js_results.append(data)
                dir_info[dirpath]['lines'] += data['lines']
                if data['lines'] > 300 and not has_readme:
                    missing_docs.add(relpath)
                if data['exports']['functions']:
                    snapshot_functions.setdefault(relpath, {})
                    for fn in data['exports']['functions']:
                        snapshot_functions[relpath][fn['name']] = fn['signature']
                if data['routes']:
                    snapshot_routes[relpath] = data['routes']
            elif filename.endswith('.py'):
                data = analyze_py_file(path)
                data['path'] = relpath
                py_results.append(data)
                dir_info[dirpath]['lines'] += data['lines']
                if data['lines'] > 300 and not has_readme:
                    missing_docs.add(relpath)
                if data['exports']['functions']:
                    snapshot_functions.setdefault(relpath, {})
                    for fn in data['exports']['functions']:
                        snapshot_functions[relpath][fn['name']] = fn['signature']
                if data['routes']:
                    snapshot_routes[relpath] = data['routes']

    # directory-level missing docs
    for dirpath, info in dir_info.items():
        rel = os.path.relpath(dirpath, root)
        if rel == '.':
            rel = '.'
        if rel.count(os.sep) <= 1 and info['lines'] > 300 and not info['has_readme']:
            missing_docs.add(rel)

    dependencies = {}
    pkg_lock = os.path.join(root, 'package-lock.json')
    if os.path.exists(pkg_lock):
        dependencies['npm'] = parse_package_lock(pkg_lock)
    pnpm_lock = os.path.join(root, 'pnpm-lock.yaml')
    if os.path.exists(pnpm_lock):
        dependencies['npm'] = parse_pnpm_lock(pnpm_lock)
    reqs = os.path.join(root, 'requirements.txt')
    if os.path.exists(reqs):
        dependencies['pip'] = parse_requirements(reqs)

    needs_update = []
    if baseline_path and os.path.exists(baseline_path):
        with open(baseline_path, 'r', encoding='utf-8') as f:
            baseline = json.load(f)
        base_funcs = baseline.get('functions', {})
        base_routes = baseline.get('routes', {})
        for path, funcs in base_funcs.items():
            current = snapshot_functions.get(path, {})
            for name, sig in funcs.items():
                if name not in current:
                    needs_update.append({'path': path, 'reason': f'missing function {name}'})
                elif current[name] != sig:
                    needs_update.append({'path': path, 'reason': f'function signature changed for {name}'})
            for name in current:
                if name not in funcs:
                    needs_update.append({'path': path, 'reason': f'new function {name}'})
        for path, routes in base_routes.items():
            current = snapshot_routes.get(path, [])
            if set(current) != set(routes):
                needs_update.append({'path': path, 'reason': 'routes changed'})

    return {
        'js': js_results,
        'python': py_results,
        'dependencies': dependencies,
        'missing_docs': sorted(missing_docs),
        'needs_update': needs_update,
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze repository')
    parser.add_argument('path', help='Path to repository')
    parser.add_argument('--baseline', help='Baseline JSON for comparison', default=None)
    args = parser.parse_args()
    result = analyze_repo(args.path, args.baseline)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
