import os
import textwrap
from scratchbot.analyze import analyze_repo

def test_js_ts_exports(tmp_path):
    content = textwrap.dedent('''
        export function foo(a: number, b: string) { return a; }
        export class Bar {}
        export interface Baz { x: number; }
        const x = 1;
    ''')
    file = tmp_path / 'mod.ts'
    file.write_text(content)
    result = analyze_repo(str(tmp_path))
    assert result['js']
    js = result['js'][0]
    func_names = [f['name'] for f in js['exports']['functions']]
    assert 'foo' in func_names
    assert 'Bar' in js['exports']['classes']
    assert 'Baz' in js['exports']['interfaces']


def test_python_public_symbols(tmp_path):
    content = textwrap.dedent('''
        def public_func(a, b):
            pass
        def _private_func():
            pass
        class PublicClass:
            pass
        class _PrivateClass:
            pass
        @app.get("/route")
        def routed():
            pass
    ''')
    file = tmp_path / 'mod.py'
    file.write_text(content)
    result = analyze_repo(str(tmp_path))
    assert result['python']
    py = result['python'][0]
    func_names = [f['name'] for f in py['exports']['functions']]
    assert 'public_func' in func_names
    assert '_private_func' not in func_names
    assert 'PublicClass' in py['exports']['classes']
    assert '_PrivateClass' not in py['exports']['classes']
    assert '/route' in py['routes']


def test_missing_docs_rule(tmp_path):
    (tmp_path / 'README.md').write_text('root readme')
    pkg = tmp_path / 'pkg'
    pkg.mkdir()
    big_file = pkg / 'big.py'
    big_file.write_text('\n'.join('print(1)' for _ in range(301)))
    result = analyze_repo(str(tmp_path))
    assert 'pkg/big.py' in result['missing_docs']
    assert 'pkg' in result['missing_docs']
