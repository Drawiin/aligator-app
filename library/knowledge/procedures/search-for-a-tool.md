# How to search for a tool

1. Turn the task into search keywords and run:
   `python3 library/tools/tool-search/cli.py search "<query>" --json`
   (ranking is deterministic: tag > name > when_to_use/helps_with >
   description).
2. If results are poor (no hits, low scores, nothing that fits), retry with
   reformulated queries: synonyms, `--tags` from the shared tag pool, `--type`
   (`research` | `execution` | `both` | `inference`). Stop after a few
   reformulations — do not loop.
3. If the envelope carries `weak_match: true`, the top hit is only a keyword
   coincidence: consider reporting that **no relevant tool exists** rather
   than forcing a pick. Recommend a weak hit only if reading its guide
   genuinely confirms fit.
4. Read `description` and `matched` for the candidates; only for the top few,
   read the tool's usage guide (the `guide` path in the hit) to confirm fit.
   Beware stubs — manifests say so in the description; never recommend a stub
   as if it worked.
5. Select the minimal tool set — usually one tool, never "everything that
   vaguely matches".

Source: .ai/agents/tool-searcher.md
