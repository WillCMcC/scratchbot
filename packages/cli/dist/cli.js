#!/usr/bin/env node
const { spawn } = require('child_process');

function runPython(mod, args) {
  const child = spawn('python', ['-m', `scratchbot.${mod}`, ...args], { stdio: 'inherit' });
  child.on('close', (code) => {
    process.exit(code ?? 0);
  });
}

const [command, ...rest] = process.argv.slice(2);

switch (command) {
  case 'analyze':
    runPython('analyze', rest);
    break;
  case 'plan':
    runPython('plan_builder', rest);
    break;
  case 'apply':
    runPython('git_ops', rest);
    break;
  default:
    console.error('Usage: scratchbot <analyze|plan|apply> [args...]');
    process.exit(1);
}
