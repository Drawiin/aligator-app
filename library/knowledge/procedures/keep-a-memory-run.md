# How to keep a memory run

Run-scoped memory lives at `.ai/memory/{run_id}.md` (canonical path), managed
with the memory CLI:

```bash
python3 library/tools/memory/cli.py write --run <run-id> --content-file progress.md
python3 library/tools/memory/cli.py write --run <run-id> --append --content "- step 2 done"
python3 library/tools/memory/cli.py read --run <run-id>
python3 library/tools/memory/cli.py list
```

`--content` stores its string verbatim (shell `\n` escapes are not newlines);
for multiline content use `--content-file <path>`, or `-` for stdin with a
heredoc:

```bash
python3 library/tools/memory/cli.py write --run <run-id> --content-file - <<'EOF'
# Progress
- step 1 done
EOF
```

Duties beyond read/write — keep memory indexable (schema in
`.ai/memory/README.md`: fixed sections, one item per line, logs in the
`{run_id}/` details folder), and **prune** outdated or wrong information;
writing new information is as important as reading. Prune steps:

1. `compact <run-id>` — merges the duplicate section headers that appends
   accumulate into one canonical section set.
2. Read the file; remove or correct stale/wrong lines (keep a one-line trace
   under `## Decisions` when a decision is reversed).
3. `write --run <run-id>` **without** `--append` to replace the whole file
   with the cleaned version.

Sessions are ephemeral because everything worth keeping is saved in the
memory folder.

Source: NEW_DIRECTION.md (§ 3. Memory); .ai/memory/README.md (schema)
