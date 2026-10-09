# Memory lives at .ai/memory/

The canonical memory path is `.ai/memory/` (per NEW_DIRECTION § Agnostic
layout; recorded as decision D-17). Run-scoped memory files are stored there —
not in `.memory/`, `.context/runs/`, or ad-hoc locations. Applies whenever an
agent persists or reads task memory.

Source: .ai/state/decisions.md (D-17)
