# Sensors run before the adversarial critic

Self-healing order is fixed: compute sensors first (lint, tests, build), then
a fresh-context adversary that assumes the implementer was wrong. The critic
gets artifacts/diff and done-criteria — not the implementer's rationalizations.
Applies to every validation pass after a worker finishes.

Source: NEW_DIRECTION.md (§ Foundation concepts — Self healing)
