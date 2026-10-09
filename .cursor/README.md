# `.cursor/` — Cursor harness adapters

Thin wrappers: each file carries Cursor's expected format, and the body points
into `.ai/`. The agent files embed this machine's absolute repo path — regenerate
them if the project is checked out somewhere else.

| Adapter | Cursor mechanism | Points to |
|---|---|---|
| `rules/mvp-agent.mdc` | Always-applied rule — a normal chat is the MVP agent | `.ai/system-prompt.md` + the three search CLIs |
| `skills/orchestrator/SKILL.md` | Agent Skill, `disable-model-invocation: true` — operator opts in with `/orchestrator` | `.ai/system-prompt.md` (same brain) |
| `agents/*.md` (6) | Project subagents (search agents `readonly: true`; worker/validator/memory need writes) | `.ai/agents/*.md` + `.ai/contracts/pipe.md` |
