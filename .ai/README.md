# `.ai/` — agnostic harness home

The orchestrator brain and the files it loads on demand. Cursor adapters in
`.cursor/` are thin wrappers that point here.

| Path | Holds |
|---|---|
| `system-prompt.md` | Orchestrator system prompt — the brain; Cursor always-on wrapper is `.cursor/rules/mvp-agent.mdc` |
| `agents/` | 6 sub-agent instruction files |
| `contracts/` | `pipe.md` — the return envelope every sub-agent uses |
| `memory/` | Live run-memory store (`{run_id}.md`; schema in its README) |
| `skills/`, `tools/`, `knowledge/` | Created on demand when a workflow needs them |
