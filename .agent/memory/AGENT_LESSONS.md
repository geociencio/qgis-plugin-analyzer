# Agent Lessons

## Latest Technical Lessons
- date: 2026-04-26
  lesson: "The Maintainability Index (MI) formula is heavily biased against long files (SLOC); refactoring monoliths like `engine.py` into smaller modules is mandatory for a stability score >50."
- date: 2026-04-26
  lesson: "Shadowing package names with module names (e.g., `cli.py` vs `cli/`) causes self-referencing circular dependency false positives in AST semantic analysis."
- date: 2026-04-26
  lesson: "Decoupling analysis from reporting (Issue B) requires a 'Freshness Check' (mtime comparison) to avoid stale data confusion."
- date: 2026-04-26
  lesson: "AST-based metrics (Issue A) should use dedicated booleans for return type detection to handle multi-line signatures robustly."

- date: 2026-04-05
  lesson: "When upgrading agentic frameworks, use `skill_sync.py` to regenerate the dynamic triggers in `AGENTS.md` automatically."
- date: 2026-04-05
  lesson: "Ruff `--fix` handles type hint deprecations proactively (`List` to `list`), validating PEP 585 compliance natively."
- date: 2026-04-05
  lesson: "The `.agent` framework strictly separates project-specific scopes (via `scaffold/qgis`) and unified logic (`skills/`)."
