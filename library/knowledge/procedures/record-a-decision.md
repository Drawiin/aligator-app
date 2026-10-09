# How to record a decision (D-NN house style)

Decisions live in `.ai/state/decisions.md` — an append-only list in
`D-NN` style, newest at the bottom:

1. Take the next `D-NN` number.
2. Append one bullet in the house format:
   `**D-NN** — _YYYY-MM-DD_ — **status** — **Short title.** Body with the
   decision and its rationale, linking the files it touches.`
3. `status` is `accepted` or `superseded by D-NN` — when a new decision
   replaces an old one, mark the old entry superseded rather than editing it
   away (the list is append-only).

Source: .ai/state/decisions.md
