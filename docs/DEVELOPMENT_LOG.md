# Development Log

## [2026-10-10] Security Restored & Deep-Analysis Hardening (v1.15.1)
- **Fixed**: Bandit-inspired security checks never ran (`security_rules` was not imported → empty registry). Now self-register on import; regression test added; `security` scope uses the real ids (`B102/B301/B307/B602/B608/HARDCODED_SECRET`).
- **Refactor**: `rules/scopes.py` is the single source of truth for scope→rule ids; removed dead code (`models/`, `modernization_rules`, unused helpers); CC cut (`run` 16→1, `visit_For` 18→1, `visit_Constant` 17→8).
- **Quality**: coverage 75%→86%, CI coverage floor 80%.
- **Docs**: README deep update; comparison moved to `docs/research/COMPARISON_VS_ALTERNATIVES.md`.

## [2026-10-10] Repo Hygiene, CLI Hardening & CI (v1.15.0)
- **Repo hygiene**: untracked generated artifacts (`AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json`, `.analyzer_state.json`, `.coverage`, `analysis.log`, …) and extended `.gitignore`; archived debug artifacts into `docs/development/`.
- **CLI robustness**: transversal `# noqa` / `# noqa: RULE_ID` opt-out; ruff audit runs via `sys.executable -m ruff` and reports `ruff_metadata.tool_unavailable`; `str`/`Path` boundary normalization.
- **Performance**: configurable workers (profile `workers` / `--workers`, default `min(4, max(1, cpu-1))`) + file batching.
- **Coverage**: ported design-pattern detection, anti-patterns (`GOD_OBJECT`, `SPAGHETTI_CODE`, `MAGIC_NUMBER`, `DEAD_CODE`), Halstead metrics and generic optimizations.
- **CI**: `.github/workflows/ci.yml` (3.11–3.13) runs `ruff check`, `ruff format --check`, `mypy src/`, `pytest --cov=analyzer --cov-fail-under=70` and the self-gate `qgis-analyzer analyze . --max-cc 15`.

### Output contract (`analysis_results/project_context.json`)
- Top-level `schema_version` + `analyzer_version`.
- `metrics.{total_files,total_lines,quality_score,maintainability_score,security_score}`.
- `ruff_findings` + `ruff_metadata` (`exit_code`, `tool_unavailable`, `command`).
- `patterns` (design patterns) and `optimizations` (`module_too_large`, `complexity_refactoring`).
- Per-module `research_metrics.{patterns,halstead}`.
- `cc_gate`/`cc_violations` embedded when `--max-cc` is used with `--json`.

### Inline suppression
- `# noqa` suppresses all rules on the line; `# noqa: RULE_ID` suppresses one rule.

## [2026-10-10] Agentic Forge Overlay Alignment
- Aligned the project overlay with `ai-context-core` (`v5.1.0`), keeping the framework pin at `v1.2.0` (`2de22cf`).
- Added 4 overlay skills under `.agent-state/skills/`: `tech-stack`, `debug-specialist`, `skill-authoring`, `release-qgis-plugin-analyzer`.
- `release-qgis-plugin-analyzer` keeps `mypy` and uses **2** version sites (`pyproject.toml` + `uv.lock`; runtime version is dynamic).
- `AGENTS.md`: overlay skills table updated (6 skills here) and documented `forge.toml [project].analyzer_command` as the self-analysis hook.
- `docs/AGENTIC_FORGE_ADOPTION.md` §6/§7 updated (ai-context-core = migrated; qgis-plugin-manager pending).
- Validation: `forge.py validate` → 15 skills (9 framework + 6 overlay), 14 workflows.

## [2026-10-08] Agentic Forge Adoption (F1–F5)
- Adopted the `agentic-forge` framework (Codeberg, `v1.2.0`) as a git submodule at `.agent/`.
- Moved project-owned state to `.agent-state/` (memory, history, `task.md`, `next_steps.md`) and overlay skills (`domain-logic`, `project-context`).
- Added `forge.toml` (`max_cc = 15`, `module_size_limit = 400`) and switched tooling to `python .agent/tools/forge.py`.
- Removed the legacy `.ai-context/` system, `scaffold/`, inherited SecInterp scripts, and the `ai-context-core` dev dependency.
- Genericized `qa-standards` → `testing-standards` (promoted upstream) and folded the `I18nVisitor` notes into `domain-logic`.
- CI: added `submodules: recursive`; `opencode.json` now discovers the overlay skills.
- Maintenance: [session_2026-10-08_agentic_forge_adoption.md](maintenance/session_2026-10-08_agentic_forge_adoption.md).

## [2026-09-14] v1.14.0: Analyzer Generalization & Qt6 Readiness
- Completed the 5-phase analyzer generalization plan (i18n AST rule, `--max-cc` gate, Python 3.11, CI output contract, tests).
- Added 11 Qt6 migration rules (`QT6_*`, `QGS4xx` parity) via a dedicated `QtTransitionVisitor`.
- Fixed type-hint coverage to count all parameter kinds; added stale-cache detection to `summary`.
- Refreshed competitive analysis (2026 ecosystem data) and resolved setuptools license deprecation warnings.
- Release: `1.14.0` (minor — new features + Python 3.11 floor).
- Maintenance: [session_2026-09-14_generalize_analyzer_v1.14.0.md](maintenance/session_2026-09-14_generalize_analyzer_v1.14.0.md).

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
