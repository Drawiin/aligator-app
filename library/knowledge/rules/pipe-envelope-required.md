# Sub-agents return via the Pipe envelope

Every sub-agent ends its reply to the orchestrator with the Pipe envelope and
nothing else: `status: success | error | blocked`, a one-line `summary`, and
`details` — inline only when the whole payload is ≤ 10 lines, otherwise an
absolute path to a details file. Never paste logs, diffs, or file contents
into the reply. Applies to every sub-agent → orchestrator return.

Source: .ai/contracts/pipe.md
