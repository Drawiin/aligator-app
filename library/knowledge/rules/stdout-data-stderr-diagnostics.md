# stdout is data, stderr is diagnostics

Tool CLIs keep stdout for data and stderr for diagnostics, and support a
`--json` flag for machine-readable output. Applies to every CLI under
`library/tools/` — never mix human chatter into the data stream.

Source: library/knowledge/procedures/build-a-tool-cli.md (CLI guidelines — stdout = data, stderr = diagnostics)
