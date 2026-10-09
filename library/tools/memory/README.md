# memory

Persist run-scoped task memory as markdown under `.ai/memory/{run_id}.md` —
the canonical location; section schema in `.ai/memory/README.md` (that file is
the store's doc — `list` excludes it). The CLI is section-agnostic by design:
agents compose the markdown, the CLI persists it.

## Usage

```bash
python3 library/tools/memory/cli.py write --run demo-01 --content "- step 1 done"
python3 library/tools/memory/cli.py write --run demo-01 --append --content-file progress.md
python3 library/tools/memory/cli.py read --run demo-01
python3 library/tools/memory/cli.py compact demo-01
python3 library/tools/memory/cli.py list
```

`--content` stores the string **verbatim** — the shell does not turn `\n`
escapes into newlines. For multiline content use `--content-file <path>`
(mutually exclusive with `--content`; `-` reads stdin, so a heredoc works):

```bash
python3 library/tools/memory/cli.py write --run demo-01 --content-file - <<'EOF'
# Progress
- step 1 done
EOF
```

Every `write` (replace or `--append`) stamps the stored block with a UTC
timestamp marker; the first write also records the run title.

`compact <run_id>` deterministically merges the partial section headers that
repeated `--append` blocks accumulate into one canonical section set (schema
order), content concatenated chronologically, timestamp markers preserved as
sub-entries; unknown sections are appended (merged by header) at the end.
`--append` semantics are unchanged — compact is a cleanup pass, e.g. before
pruning.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Error (e.g. content file exists but cannot be read) |
| 2 | Run not found (read, compact) |
| 3 | Invalid input/usage (missing/unknown arguments, `--content` and `--content-file` together, content file missing) |
