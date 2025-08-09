# ScratchBot CLI

Command line interface for running ScratchBot helpers.

## Usage

Install dependencies and use the `scratchbot` command:

```bash
scratchbot analyze [path]
scratchbot plan [path]
scratchbot apply [...args]
```

Each subcommand forwards to the corresponding Python module under the
`scratchbot` package.
