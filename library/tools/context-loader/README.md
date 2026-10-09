# context-loader

Suggest relevant files for the current task before expensive inference —
keyword match on paths/filenames; an optional `.context/manifest.json`
(`{"files": [...]}`) boosts listed paths. Related:
[`knowledge-search`](../knowledge-search/) finds **passages**; this tool
suggests **files**. Both stay as-is; a merge is possible later.

## Usage

```bash
python3 library/tools/context-loader/cli.py load --task "spec validation" --root .
python3 library/tools/context-loader/cli.py load --task "memory write" --json --limit 10
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 2 | No matches |
| 3 | Invalid input/usage (missing/unknown arguments, invalid root, --limit < 1) |
