# How to build a tool (manifest + CLI)

Every tool under `library/tools/<name>/` follows the two-layer anatomy —
discovery stays lean, invocation detail stays out of the search index:

1. **Manifest** (`tool.json`) — search/discovery only. Required fields:
   `name`, `description` (new-hire framing), `type`
   (`research` | `execution` | `both` | `inference`), `tags` (from the shared
   controlled pool — reuse over near-duplicates), `when_to_use` (short trigger
   phrases, array), `helps_with` (one sentence: why this beats improvising).
   Optional later: `status`, `side_effects`, `guide` path when the guide is
   not the tool's README. Stubs say so in their descriptions.
2. **Usage guide** — the tool's `README.md` (official convention; a separate
   `USAGE.md` is an optional future split): commands, flags, examples,
   gotchas / when not to use.
3. **`cli.py`** — all behavior lives here.
4. **Shim** — a same-named 2-line executable
   (`#!/bin/sh` + `exec python3 "$(dirname "$0")/cli.py" "$@"`); no logic, so
   shim and `cli.py` can never drift.

**Wrapper-only tools are first-class**: manifest + guide can describe an
external CLI (`gh`, `adb`, …) with no custom code in-repo.

## CLI guidelines

Condensed from Anthropic's [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents),
Ronacher's agentic-coding posts, and project research:

- **`--help` is the discovery surface** — include copy-paste examples agents
  can run immediately.
- **stdout = data, stderr = diagnostics** — support `--json` for
  machine-readable output.
- **Semantic exit codes beyond 0/1** — `0` success, `1` error, `2` not found,
  `3` invalid input.
- **Budget output tokens** — concise defaults; pagination, filtering, and
  `--limit` for large results (the in-repo search CLIs implement this as
  `--limit` + capped snippets).
- **Summarization / progressive disclosure** — default output small and
  focused (success/failure first, details on demand); strip log noise; prefer
  deterministic filter/summarize scripts, LLM summarization only after that
  and rarely.
- **Cache costly results** — especially remote fetches and tools with an LLM
  step; keep a recent/latest result when re-running is expensive.
- **Queue shared resources** — when multiple agents/skills write the same
  files (memory, state), use a wait queue (SQLite-style) so writes don't
  conflict.
- **Inference tools** — `type: inference` when the primary job is LLM judgment
  (scripts invoking Claude/Codex/Cursor CLIs or an API), e.g. summarizing,
  decisions, non-deterministic mapping. Prefer computation; reach for
  inference when deterministic mapping fails. Still a lean manifest — no
  extra schema fields.
- **Prescriptive errors** — tell the agent what to do next, not just what
  failed.
- **Consolidate workflows** — one high-impact tool beats many 1:1 API wraps.
- **No interactive prompts** — `--yes`, `--dry-run`, explicit flags instead.
- **Stateless / idempotent** — persist state in files (`.ai/memory/`,
  manifests), not in-process.
- **High-signal fields** — names and paths, not raw UUIDs; resolve IDs when
  possible.
- **Unambiguous naming + namespace** — prefix by domain (`memory read`, not
  `read`).
- **Eval-driven tool quality** — measure accuracy, tool-call count, tokens,
  error rate; iterate. Description quality beats fancy retrieval for small
  catalogs.
- **CLI over MCP for most chat workflows** — agents already know shell; MCP
  loads tool definitions upfront ([Ronacher, Jun 2025](https://lucumr.pocoo.org/2025/6/12/agentic-coding/));
  CLIs are discovered lazily via `--help` ([Ronacher, Nov 2025](https://lucumr.pocoo.org/2025/11/21/agents-are-hard/)).
- **Private data stays inside the tool's own directory** — `.data/` (caches,
  metadata), `.secrets/` (credentials; dir `chmod 700`, files `600`), `.venv/`
  (own interpreter/deps). Never at repo root, never committed; all three
  gitignored, created on demand.

Tags are a **controlled vocabulary** (shared pool — e.g. `github`, `git`,
`pr`, `context`, `memory`, `mobile`, `testing`); `tool-search` filters/boosts
by tag, then ranks on name / `when_to_use` / `helps_with` / description.
Background: [tool-search landscape](../../../references/external-sources/summaries/10-tool-search.md).

Source: library/tools/README.md (anatomy + conventions); NEW_DIRECTION.md (§ Foundation concepts — Tool concepts)
