# `library/knowledge/` — global knowledge base

Global, reusable knowledge for the 3-tool model (`NEW_DIRECTION.md` § 2), using
the decided taxonomy (D-14: Procedures and How-tos collapsed):

- **Rules** — simple constraints agents must follow ("never do X", "always use
  pattern Y"), including very specific edge cases like PR patterns.
- **Procedures** — how to do certain things, from small hints/tips up to
  specific how-tos. When a procedure grows too big, it graduates to an
  Inferential tool.

One entry per file; kebab-case filenames are the search surface; every entry
ends with a `Source:` line pointing at the repo document it encodes. Searched
by [`knowledge-search`](../tools/knowledge-search/) (`--category
rules|procedures` scopes to one category); project-local / workflow knowledge
lives in `.ai/knowledge/` instead (two canonical places, D-14).

## Inventory

### [`rules/`](rules/)

| File | Constraint |
|---|---|
| [`absolute-paths-at-runtime.md`](rules/absolute-paths-at-runtime.md) | Agents build absolute paths at runtime; instruction files stay repo-root-relative |
| [`archived-references-stay-unedited.md`](rules/archived-references-stay-unedited.md) | `references/archive/` is historical — never rewrite it |
| [`computation-before-inference.md`](rules/computation-before-inference.md) | Prefer deterministic computation over LLM inference |
| [`keep-context-small-load-on-demand.md`](rules/keep-context-small-load-on-demand.md) | Small, focused context; load everything else on demand |
| [`memory-lives-in-ai-memory.md`](rules/memory-lives-in-ai-memory.md) | Canonical memory path is `.ai/memory/` (D-17) |
| [`orchestrator-never-does-work.md`](rules/orchestrator-never-does-work.md) | Orchestrator always delegates to fresh sub-agents |
| [`pipe-envelope-required.md`](rules/pipe-envelope-required.md) | Sub-agents return via the Pipe envelope; inline details ≤ 10 lines |
| [`semantic-exit-codes.md`](rules/semantic-exit-codes.md) | CLIs use exit codes 0 success / 1 error / 2 not found / 3 invalid input |
| [`sensors-before-adversarial-review.md`](rules/sensors-before-adversarial-review.md) | Compute sensors first, then the fresh-context critic |
| [`stdout-data-stderr-diagnostics.md`](rules/stdout-data-stderr-diagnostics.md) | stdout = data, stderr = diagnostics, `--json` supported |
| [`study-files-are-personal.md`](rules/study-files-are-personal.md) | `STUDY*.md` is personal and git-ignored — project state goes to `.ai/state/` |
| [`tool-private-data-stays-in-tool-dir.md`](rules/tool-private-data-stays-in-tool-dir.md) | `.data/` / `.secrets/` / `.venv/` stay inside the tool dir, never committed |
| [`tool-shims-contain-no-logic.md`](rules/tool-shims-contain-no-logic.md) | Executables are 2-line exec shims; all logic in `cli.py` |
| [`worker-never-certifies-own-work.md`](rules/worker-never-certifies-own-work.md) | Independent validator judges; PASS needs evidence |

### [`procedures/`](procedures/)

| File | How-to |
|---|---|
| [`build-a-tool-cli.md`](procedures/build-a-tool-cli.md) | Build a tool: manifest + cli.py + shim + README, and the full CLI guidelines |
| [`keep-a-memory-run.md`](procedures/keep-a-memory-run.md) | Write/append/read run memory; keep it indexable, compact + prune stale entries |
| [`record-a-decision.md`](procedures/record-a-decision.md) | Append a `D-NN` entry to `.ai/state/decisions.md` in the house style |
| [`run-validated-unit-of-work.md`](procedures/run-validated-unit-of-work.md) | Worker executes, validator judges, both return via Pipe |
| [`search-for-a-tool.md`](procedures/search-for-a-tool.md) | tool-search invocation + reformulation + minimal tool set |
| [`search-for-knowledge.md`](procedures/search-for-knowledge.md) | knowledge-search invocation + reformulation + aggressive curation |
