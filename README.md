# ScratchBot

## Prerequisites

- Python 3.11+
- Node.js for JavaScript and TypeScript analysis
- TypeScript compiler (`tsc`)
- Optional: GitHub token via the `GITHUB_TOKEN` environment variable

## Typical Workflow

1. **Run the analyzer** to scan the repository:
   ```bash
   python -m scratchbot.analyze .
   ```
   Expected output (truncated for clarity):
   ```json
   {
     "exports": {"functions": [], "classes": []},
     "lines": 42,
     "routes": []
   }
   ```

2. **Generate a documentation plan** with a model call (mocked here):
   ```python
   from scratchbot import assemble_context, generate_docs_plan

   context = assemble_context(".")
   plan = generate_docs_plan(context, lambda prompt: '{"missing": [], "needs_update": []}')
   print(plan)
   ```
   Expected output:
   ```
   {'missing': [], 'needs_update': []}
   ```

3. **Commit changes** using `git_ops.commit_changes`:
   ```python
   from scratchbot import commit_changes

   commit_changes(".", ["README.md"], "docs: update {path}")
   ```
   Verify the commit manually:
   ```bash
   git log -1 --stat
   ```

### Troubleshooting

- Analyzer errors about missing `node` or `tsc`: install Node.js and the TypeScript compiler and ensure they are in your `PATH`.
- `assemble_context` raising `context exceeds token limit`: reduce the size of your diff or exclude large files.
- Permission errors during commit: ensure your Git configuration is correct and you have write access.
- For GitHub operations requiring authentication, define `GITHUB_TOKEN` in your environment.
