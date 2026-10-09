# How to run a validated unit of work

The worker/validator pair is how work gets proven (*Self healing* /
*Independent Judge*):

1. The orchestrator assembles the assignment: the task with its done criteria
   (Done Contract), the context selected for the task, and the allowed tools —
   then forwards it to a fresh **worker**.
2. The worker restates the done criteria to itself, does exactly that work,
   runs the cheap sensors it was given (lint, tests, build), and returns via
   the Pipe envelope — reporting what it did and what the sensors said, never
   certifying its own work. If the assignment is missing context, tools, or
   criteria it genuinely needs, it returns `blocked` naming what — it never
   guesses.
3. The **validator** then judges in a fresh context: sensors first, then an
   adversarial read against the done contract, hunting for what the worker
   missed — unverified behaviours, edge cases, rule/procedure violations,
   scope creep, claims not backed by the artifacts. It gets artifacts and
   criteria, not the worker's rationalizations. Every gap — and every PASS —
   needs evidence. `status: success` only when no gaps were found.
4. The validator fixes nothing; the orchestrator routes healing (rerun,
   forward, or reflect) from the Pipe returns.

Source: NEW_DIRECTION.md (§ Way of working)
