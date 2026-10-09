# `.ai/memory/` — run memory store

One markdown file per run, `{run_id}.md`, managed by the memory CLI
(`library/tools/memory/` — write / append / read / list / compact) and
maintained by the memory sub-agent. Fixed sections keep runs indexable:

- `## Task state` — `[ ]`/`[x]` todos, current status, next step
- `## Decisions` — one per line: what was decided + why
- `## Notes` — findings, patterns to follow, pointers

Rules:

- Plain text, **one item per line** — grep-able; no prose walls or pasted logs
  (those go in a companion `{run_id}/` details folder next to the run file).
- Append during a session (`write --append`); multiline content via
  `--content-file` (`--content` keeps shell `\n` escapes literal).
- `compact {run_id}` merges the duplicate section headers appends accumulate —
  run it before reading a long run or pruning.
- **Prune** stale or wrong entries (compact → read → clean → replace-write):
  a duty, not an option — wrong memory poisons every later run.
