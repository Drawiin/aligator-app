# Semantic exit codes beyond 0/1

Tool CLIs use semantic exit codes beyond plain 0/1: `0` success, `1` error,
`2` not found (no results), `3` invalid input. Applies when building or
invoking any CLI under `library/tools/` — agents branch on the code instead
of parsing error text.

Source: library/knowledge/procedures/build-a-tool-cli.md (CLI guidelines — semantic exit codes)
