# Development Log

## [2026-09-14] v1.14.0: Analyzer Generalization & Qt6 Readiness
- Completed the 5-phase analyzer generalization plan (i18n AST rule, `--max-cc` gate, Python 3.11, CI output contract, tests).
- Added 11 Qt6 migration rules (`QT6_*`, `QGS4xx` parity) via a dedicated `QtTransitionVisitor`.
- Fixed type-hint coverage to count all parameter kinds; added stale-cache detection to `summary`.
- Refreshed competitive analysis (2026 ecosystem data) and resolved setuptools license deprecation warnings.
- Release: `1.14.0` (minor — new features + Python 3.11 floor).

## [2026-09-14] Fase 0: CI Output Contract & i18n Generalization Plan
- Analyzed `docs/plans/` (upstreaming plan + i18n AST reference) against the current codebase; identified broken reference path, TOML-array parser gap, and missing inline comment suppression.
- Implemented Fase 0 of analyzer generalization: `schema_version`/`analyzer_version`, `--include-content`, `--json`, and legacy output-dir warning.
- Created `docs/plans/implementation_plan_generalize_analyzer.md` (5-phase plan; decisions: keep `MISSING_I18N` id, bump Python to 3.11).
- Maintenance: [session_2026-09-14_output_contract_i18n.md](maintenance/session_2026-09-14_output_contract_i18n.md).

## [2026-05-25] v1.13.2: I18n False Positive Fix
- Released version `1.13.2` fixing ~80% of i18n false positives in projects using `QCoreApplication.translate()`.
- Added `I18N_WRAPPER_FUNCTIONS` and `_in_i18n_wrapper` state tracking to `I18nVisitor`.
- Added 11 test cases for i18n wrapper recognition (self.tr, translate in static methods, super().__init__, format chains).
- Upgraded agentic system from Gen 5 to Gen 6: observability, 3-tier memory lifecycle, CodeWhale runtime bridge.
- Created `scripts/sync_metrics.py` for automated self-analysis and metric tracking.

## [2026-04-26] v1.13.1: Metadata Synchronization
- Released version `1.13.1` to ensure consistency across all distribution artifacts.
- Synchronized `README.md` metrics and project metadata in build packages and GitHub releases.

## [2026-04-26] v1.13.0: Quality Blindage & Architectural Refactor
- Released version `1.13.0` on GitHub with 76% global test coverage.
- Decomposed `StandardsVisitor` into `I18nVisitor` and extracted `ScoringEngine`.
- Blinded AST Visitors with >95% coverage across all core auditing rules.
- Fixed Maintainability scoring bug by incorporating internal AST violations.
- Standardized the entire agentic system to English and adapted for generic projects.

## [2026-04-26] v1.12.0: Gen 5 Architecture & Precision Analytics
- Released version `1.12.0` on GitHub with complete build assets.
- Resolved cache staleness by implementing modification time comparison in `handle_summary`.
- Refactored `metrics_visitor.py` to fix false positive missing type hints on multi-line signatures.
- Modernized all workflows and documentation to Gen 5 (English-first) standards.
- Updated `README.md` and `CHANGELOG.md` with new features and metrics.

## [2026-04-26] Summary: Technical Audit of Inconsistencies
- Analyzed `bugreport.md` regarding Type Hint detection and Cache Staleness.
- Investigated `MetricsVisitor`, `ScoringEngine`, and `SummaryCommand` logic.
- Confirmed absence of "Freshness Check" in `summary` command.
- Validated AST-based type hint detection on multi-line signatures.
- Documented findings and prepared execution plan for future fixes.


## [2026-04-05] Resumen: Modernization to Gen 5 Agentic Framework
- Synchronized specialized skills and workflows from Antigravity Gen 5 framework.
- Applied rigorous automated code format check and fixed minor linter errors.
- Exported global CLI configurations to MCP standards (`scripts/` and `scaffold/` imported).
