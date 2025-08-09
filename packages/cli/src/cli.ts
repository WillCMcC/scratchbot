#!/usr/bin/env node
import { spawn } from 'child_process';

function runPython(mod: string, args: string[]): void {
  const child = spawn('python', ['-m', `scratchbot.${mod}`, ...args], { stdio: 'inherit' });
  child.on('close', (code: number | null) => {
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
