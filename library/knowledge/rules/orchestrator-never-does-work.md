# Orchestrator never does work itself

The orchestrator never performs work itself — it always delegates to fresh
sub-agents. Applies whenever the orchestrator is tempted to execute, read
files at length, or summarize: route it to a worker instead.

Source: NEW_DIRECTION.md (§ The model)
