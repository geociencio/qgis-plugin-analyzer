# Active Task: Technical Debt & Refactoring

## Status
- [ ] **Technical Debt**: Extract `ScoringEngine` from `src/analyzer/engine.py` to `src/analyzer/scoring.py`.
- [ ] **Technical Debt**: Rename `src/analyzer/cli.py` to `src/analyzer/cli_handler.py` to resolve circular dependency with the `cli/` package.
- [ ] **Documentation**: Update `RULES.md` to reflect Gen 5 architecture.
- [ ] **Maintenance**: Check PyPI release status.

## Completed (v1.12.0)
- [x] Fix Cache Staleness in `summary` command.
- [x] Improve Multi-line Type Hint reporting in `MetricsVisitor`.
- [x] Update README and CHANGELOG for v1.12.0.

## Context
- The project has reached v1.12.0.
- Module Stability is < 50, requiring refactoring of `engine.py`.
- Circular dependency issues detected between `src/analyzer/cli.py` and `src/cli/`.
