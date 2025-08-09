const fs = require('fs');
const ts = require('typescript');

function analyzeFile(file) {
  const sourceText = fs.readFileSync(file, 'utf8');
  const sourceFile = ts.createSourceFile(file, sourceText, ts.ScriptTarget.Latest, true);
  const exports = {functions: [], classes: [], interfaces: []};

  function hasExportModifier(node) {
    return (ts.getCombinedModifierFlags(node) & ts.ModifierFlags.Export) !== 0;
  }

  function visit(node) {
    if (ts.isFunctionDeclaration(node) && node.name && hasExportModifier(node)) {
      const params = node.parameters.map(p => {
        if (ts.isIdentifier(p.name)) {
          return p.name.text;
        }
        return p.name.getText();
      }).join(',');
      exports.functions.push({name: node.name.text, signature: `(${params})`});
    } else if (ts.isClassDeclaration(node) && node.name && hasExportModifier(node)) {
      exports.classes.push(node.name.text);
    } else if (ts.isInterfaceDeclaration(node) && node.name && hasExportModifier(node)) {
      exports.interfaces.push(node.name.text);
    }
    ts.forEachChild(node, visit);
  }

  visit(sourceFile);

  const lines = sourceText.split(/\r?\n/).filter(l => l.trim() !== '').length;

  const routeRegex = /\b(app|router)\.(get|post|put|delete|patch)\(\s*['"`]([^'"`]+)['"`]/g;
  const routes = [];
  let m;
  while ((m = routeRegex.exec(sourceText)) !== null) {
    routes.push(m[3]);
  }

  return {exports, lines, routes};
}

const file = process.argv[2];
if (!file) {
  console.error('No file provided');
  process.exit(1);
}
const result = analyzeFile(file);
process.stdout.write(JSON.stringify(result));
