# Pipe return contract

Every sub-agent ends its reply to the orchestrator with this envelope — and
nothing else:

```
status: success | error | blocked
summary: <one line — what happened>
details: <inline block (≤ 10 lines) for tiny results, OR absolute path to a details file>
```

- Never paste logs, diffs, or file contents into the reply. Anything beyond
  the summary goes in `details` — inline only when the whole payload is ≤ 10
  lines, otherwise a details file (written where the orchestrator told you,
  e.g. the run's `.ai/memory/{run_id}/` folder), never both. Omit `details:`
  when the summary says everything.
- `error`: the summary names what failed **and the next action to try**;
  evidence goes in the details file. `blocked`: the summary names exactly
  what missing input only the orchestrator or operator can give.
- The orchestrator routes on `status` + `summary`, opening details only when
  the next decision needs them.
