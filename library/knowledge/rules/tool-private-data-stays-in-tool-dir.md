# Tool private data stays inside the tool's directory

Anything a tool saves (cached outputs, credentials, venvs, index/metadata)
lives in reserved per-tool dirs — `.data/` (caches, metadata), `.secrets/`
(credentials; dir `chmod 700`, files `600`), `.venv/` — inside the tool's own
directory. Never at repo root, never committed; all three are gitignored and
created on demand. Applies to every tool under `library/tools/`.

Source: library/knowledge/procedures/build-a-tool-cli.md (CLI guidelines — private data)
