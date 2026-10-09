# Absolute paths at runtime

At runtime an agent resolves the repo root and builds absolute paths before
acting on files and folders — this avoids errors and confusion. Instruction
files themselves keep repo-root-anchored relative paths so the harness stays
portable across machines and checkouts. Applies to every agent file operation.

Source: NEW_DIRECTION.md (§ Constraints and notes)
