# Keep context small; load on demand

Keep the agent's context as small and focused as possible — too much
information, or information not needed for the task, poisons the context and
causes hallucinations and wrong results. Main instructions stay in the system
prompt; everything else is loaded on demand via tools or memory. Applies
whenever assembling context for any agent or sub-agent.

Source: NEW_DIRECTION.md (§ Foundation concepts — Keep context small)
