# CODEBUDDY.md

@AGENTS.md

This project uses AGENTS.md as the single source of truth for all AI coding agents.
The `@AGENTS.md` import above pulls in the full ruleset.

For Codebuddy-specific extensions or notes, add them below this line.

## Codebuddy-Specific Notes

- Prefer using the `Read` and `Grep` tools before making assumptions about the codebase
- When running tests, always use `uv run pytest` (not bare `pytest`)