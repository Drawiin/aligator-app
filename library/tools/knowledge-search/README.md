# knowledge-search

Deterministic entry point over project knowledge — the interface behind the
**Knowledge search** tool in the 3-tool model. Backing (decided): text files +
the graphify index — `search` combines `graphify query` (when
`graphify-out/graph.json` exists) with ripgrep; `grep` is a targeted ripgrep
pass-through. Default roots: `references/`, `library/docs/`,
`library/knowledge/` (+ `.ai/knowledge/` once it exists).
`--category rules|procedures` scopes to `library/knowledge/<category>/`
(+ `.ai/knowledge/<category>/` when on disk). Related:
[`context-loader`](../context-loader/) suggests **files** by path keyword;
this tool finds **passages**.

## Usage

```bash
python3 library/tools/knowledge-search/cli.py search "context engineering"
python3 library/tools/knowledge-search/cli.py search "tool manifest" --json --limit 10
python3 library/tools/knowledge-search/cli.py search "exit codes" --category rules --json
python3 library/tools/knowledge-search/cli.py grep "Independent Judge" --roots library/knowledge
```

JSON hits: `path`, `line`, `snippet` (truncated to 200 chars), `source`
(`graphify` | `rg`), plus a `graphify` status field in the envelope.

## Merge policy (search)

Deterministic, in this order: graphify hits are filtered to the requested
roots; graphify title hits fill at most floor(limit/2) slots so rg content
hits are never squeezed out; rg hits (ranked by distinct query tokens per
line) fill the remainder; leftover graphify hits backfill only when rg runs
short; duplicates removed on `(path, line)`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Tooling error (rg missing, rg/graphify failed) |
| 2 | No hits |
| 3 | Invalid input/usage (missing/unknown arguments, empty query, bad root, category not on disk, --limit < 1) |
