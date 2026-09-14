# Session 2026-09-14: Analyzer Generalization — Fase 0 (CI Output Contract)

## Objectives
- Analyze `docs/plans/` (upstreaming plan + i18n AST reference) against the current codebase.
- Produce an actionable implementation plan for generalizing the analyzer to any QGIS plugin.
- Implement Fase 0: a reliable CI output contract (`project_context.json`).

## What Was Done

### Analysis of the Plans
Cross-referenced `upstreaming_qgis_analyzer.md` and `i18n_ast_rule.py` against the code, identifying:
- Broken reference: plan points to `scripts/upstream/i18n_ast_rule.py` (does not exist); the reference actually lives in `docs/plans/i18n_ast_rule.py`.
- The minimal TOML parser (`config_utils.py`) cannot parse arrays, which would silently drop the proposed `extra_ignore_calls`/`extra_exact_ignores` config on Python <3.11.
- No inline comment suppression (`# no-i18n`/`# noqa`) exists anywhere in `src/` (confirmed by grep).
- `modules[].content` is written unconditionally (`scanner.py`), confirming the source-leak prerequisite.
- `functions[].complexity` already exists (`ast_utils.py`), so the CC gate is trivial.

### Implementation Plan
Created `docs/plans/implementation_plan_generalize_analyzer.md` (5 phases) with two resolved decisions:
1. Keep the `MISSING_I18N` rule id (replace its heuristic) to avoid touching scope maps/reporters.
2. Raise `requires-python >= 3.11` to rely on stdlib `tomllib` instead of extending the minimal parser.

### Fase 0 — CI Output Contract (implemented)
- `aggregators.py`: embed `schema_version` (1) + `analyzer_version` in the JSON context.
- `engine.py` + `scanner.py`: `--include-content` flag; module source omitted by default (drop ~468 KB → ~20-30 KB, no source leak).
- `cli/commands/analyze.py` + `commands.py`: `--json` flag emitting pure JSON to stdout.
- `performance_utils.py` + `commands.py`: `set_progress_quiet()` and `_route_logs_to_stderr()` to keep stdout machine-readable.
- `commands.py`: `_warn_legacy_output_dir()` detects legacy `json/project_context.json`.

### Commits
- `7a969ad` feat(analyzer): add CI output contract
- `a8cfd50` docs(i18n): add upstreaming plan, AST reference and i18n gap analysis

## Quality Gates
| Gate | Result |
|------|--------|
| Tests | 87/87 ✅ |
| Ruff | Clean ✅ |
| Mypy | Clean (changed files) ✅ |
| `--json` stdout purity | Valid JSON, no log pollution ✅ |
| `--include-content` toggle | content key present only with flag ✅ |

## Key Decisions
1. Keep `MISSING_I18N` id (back-compat) instead of introducing `UNTRANSLATED_STRING`.
2. Raise Python floor to 3.11 (use `tomllib`) rather than extending the minimal TOML parser.
3. `--json` routes all console output (logger + progress) to stderr to preserve stdout purity.

## Next Session
1. Relocate reference: `git mv docs/plans/i18n_ast_rule.py scripts/upstream/i18n_ast_rule.py`.
2. Fase 1: port `I18nAstVisitor` into `I18nVisitor`.
3. Fase 2: `--max-cc` gate.
4. Fase 3: Python 3.11 bump + remove `_minimal_toml_load`.
