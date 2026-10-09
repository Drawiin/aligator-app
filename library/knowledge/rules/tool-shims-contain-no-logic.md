# Tool shims contain no logic

Every tool dir ships a same-named executable that is a 2-line exec shim
(`#!/bin/sh` + `exec python3 "$(dirname "$0")/cli.py" "$@"`). Shims contain no
logic, so shim and `cli.py` can never drift; behavior decisions live in
`cli.py` only. Applies when creating or editing any tool executable.

Source: library/knowledge/procedures/build-a-tool-cli.md (anatomy — shim)
