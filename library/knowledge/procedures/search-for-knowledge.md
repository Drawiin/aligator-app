# How to search for knowledge

1. Turn the need into a query and run:
   `python3 library/tools/knowledge-search/cli.py search "<query>" --json`
   The CLI combines the graphify index with ripgrep over the knowledge roots
   (`references/`, `library/docs/`, `library/knowledge/`, plus
   `.ai/knowledge/` when it exists). Add `--category rules|procedures` to
   scope to one knowledge category.
2. If results are poor, retry: reformulate keywords, use
   `python3 library/tools/knowledge-search/cli.py grep "<pattern>"` for exact
   phrases, narrow `--roots`. Stop after a few reformulations — do not loop.
3. Open only the most promising hits and read only the relevant sections.
4. Curate aggressively: dedupe overlapping hits, drop anything that does not
   answer the need, keep only passages with `path:line` provenance. When in
   doubt, leave it out — bad curation poisons the orchestrator's context.

Source: .ai/agents/knowledge-searcher.md
