# tool-search

Discover harness tools by indexing the lean `tool.json` manifests under
`library/tools/*/`. Deterministic scoring — tag exact match > name >
`when_to_use` / `helps_with` > description; text fields match whole words
only. Usage guides are read *after* ranking, never indexed.

## Usage

```bash
python3 library/tools/tool-search/cli.py list
python3 library/tools/tool-search/cli.py search "save task state" --json
python3 library/tools/tool-search/cli.py search "run tests" --tags gradle,testing --limit 3
python3 library/tools/tool-search/cli.py search "summarize" --type inference
```

Search hits (JSON): `name`, `type`, `score`, `matched` (why), `description`,
`guide` (**absolute** path to the tool's README). Both `--json` envelopes
include a `skipped` array for tool dirs whose manifest is missing or
unparseable — empty means the whole catalog was indexed.

## Weak-match signal

When the top hit's score falls below **15**, the envelope gains
`"weak_match": true` plus a one-line `"note"`: no strong match exists and
"no relevant tool" is a legitimate answer (text mode prints the same note).
Rationale from the observed score distribution (T-06): real matches ~25–45,
keyword coincidences 2–8; below 15 a hit cannot combine two meaningful
signals. Exit codes unchanged: 0 with hits (weak or not), 2 with zero hits.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success (even when some manifests were skipped) |
| 1 | No manifest could be loaded (catalog unreadable) |
| 2 | No tools matched |
| 3 | Invalid input/usage (missing/unknown arguments, empty query, unknown --type, --limit < 1) |
