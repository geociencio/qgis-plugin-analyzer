# Development Log

## [2026-10-25] Release v1.18.0 — Ignore-aware Analysis
- **Achievement**: Released the ignore-aware analysis minor: ordered `.gitignore`/`.qgisignore`/`.analyzerignore` support, `--exclude`/`--scope`, and default `docs/`/`tests/` exclusions.
- **Changes**:
    - Bumped `pyproject.toml` and `uv.lock` to `1.18.0`; verified `qgis-analyzer --version`.
    - Moved `CHANGELOG.md` `[Unreleased]` to `[1.18.0] - 2026-10-25`; added `docs/releases/notes/v1.18.0.md` and `docs/GITHUB_RELEASE_v1.18.0.md`.
    - Refreshed README “What's New” and release notes; synced `.agent-state/memory/agent_metrics.json`.
- **Quality**: 283 tests (89.33% coverage); `ruff check` + `mypy src/` clean; self-analysis `--max-cc 15` green with 10 LOW findings; Module Stability 54.0 · Maintainability 99.9 · Security 100.0.
- **Release**: **v1.18.0 published** on GitHub and PyPI (CI `publish-pypi`) on 2026-10-25.

## [2026-10-25] Ignore Files, Default Excludes & CLI Scopes
- **Achievement**: Made project discovery honor `.gitignore`, `.qgisignore` and `.analyzerignore` with ordered/negation semantics, added `--exclude` and `--scope`, and excluded `docs/`/`tests/` by default.
- **Changes**:
    - `IgnoreMatcher` now evaluates patterns in order with `!` negation (last match wins) and supports anchored, directory, basename and basic `**` patterns.
    - `ProjectAnalyzer` merges defaults → `.gitignore` → `.qgisignore` → `.analyzerignore` → profile/CLI `exclude`; `refresh_ignore_patterns()` applies CLI overrides after construction.
    - `analyze --scope` (compatible with `analyze [scope] [path]`), `--exclude` on `analyze`/`security`/`fix`, and profile `exclude`.
    - Default excludes now include `docs/` and `tests/`, so source-tree size and analysis focus on plugin code; `!docs/` re-includes.
- **Quality**: 283 tests (coverage 89%); `ruff check` + `mypy src/` clean; self-analysis `--max-cc 15` green with 10 LOW findings; Module Stability 54.0 · Maintainability 99.9 · Security 100.0.

## [2026-10-25] Release v1.17.0 — Portal Gate Integration
- **Achievement**: Prepared the v1.17.0 minor release with Flake8 support, real Bandit/detect-secrets/Flake8 adapters, the `security --json` contract, the portal profile, five `METADATA_*` rules and the 25 MB source-tree rule moved to informational.
- **Changes**:
    - Bumped `pyproject.toml` and `uv.lock` to `1.17.0`; verified `qgis-analyzer --version` reports `1.17.0`.
    - Moved `CHANGELOG.md` `[Unreleased]` to `[1.17.0] - 2026-10-25`; added `docs/releases/notes/v1.17.0.md` and the CI release body `docs/GITHUB_RELEASE_v1.17.0.md`.
    - Refreshed README badges/“What's New”, regenerated `RULES.md` (56 rules) and synced `.agent-state/memory/agent_metrics.json`.
- **Quality**: 273 tests (89.09% coverage); `ruff check` + `mypy src/` clean; self-analysis `--max-cc 15` green with 10 LOW findings; Module Stability 54.1 · Maintainability 99.9 · Security 100.0.
- **Release**: **v1.17.0 published** on GitHub and PyPI (CI `publish-pypi`) on 2026-10-25.

## [2026-10-25] Upstream Gate Integration (analyzer P0 + P1)
- **Achievement**: Implemented the qgis-analyzer slice of the portal gate integration: Flake8 support, real Bandit/detect-secrets/Flake8 adapters, a machine-readable `security` report, the security-scope/`--deep` fix, the 25 MB source-tree rule moved to informational, the portal profile and five `METADATA_*` rules.
- **Changes**:
    - New `flake8_audit.py`; `analyze --flake8` / `--linters ruff,flake8` with `flake8_findings` + `flake8_metadata` in the JSON contract.
    - New `bandit_audit.py`, `detect_secrets_audit.py`, `metadata_audit.py` and `security_audit.py`; `security --tools native|bandit|detect-secrets|flake8 --json --fail-on ...` with merged/deduplicated findings and explicit `tool_unavailable` (exit `2`).
    - `security` now runs `scope="security"` and respects `--deep` (native entropy opt-in); high findings map to `critical`/blocking.
    - Portal profile (`linters`, `security_tools`, `security_fail_on`, `metadata_rules`, `fail_on`) with CLI > profile > default precedence; `analyze --profile portal` applies the security gate.
    - Five catalog-backed `METADATA_*` rules (repository, version, QGIS4, supportsQt6, category) in the `metadata` scope; `RULES.md` now lists 56 rules.
    - Source-tree size is a warning (`constraint_warnings`); the portal 25 MB limit stays with the ZIP artifact layer. QGIS score no longer penalizes source-tree size.
    - Optional extras `[flake8]`, `[security]`, `[portal]`; README/CHANGELOG/user-guide updates.
    - `--json` logs/progress stay on stderr (including the analyzer project-type line).
- **Quality**: 273 tests (coverage 89%); `ruff check` + `mypy src/` clean; self-analysis `--max-cc 15` green with 10 LOW findings; Module Stability 54.1 · Maintainability 99.9 · Security 100.0.
- **Notes**: qgis-manage's `validate --zip` / artifact layer is implemented in the sibling repository (v0.13.0+); remaining P2 items (JSON schema snapshots, real-tool CI, `flake8_config`) are recorded in `docs/research/upstream_gate_integration.md`.

## [2026-10-19] Agentic Forge v1.4.2 & Repository Audit
- **Achievement**: Audited the repository and the shared `agentic-forge` framework, produced the analysis reports, and upgraded `.agent` from `v1.2.0` to `v1.4.2` with the new project-command contract and strict validation.
- **Changes**:
    - Added `docs/reports/DEEP_ANALYSIS_v1.16.0_REPOSITORY_AUDIT.md` and the agentic-forge baseline/delta reports (`v1.2.0`, `v1.3.0`, `v1.4.1`, `v1.4.2`).
    - `.agent` bumped through `v1.3.0` (`b41facd`), `v1.4.1` (`a98f5a8`) and `v1.4.2` (`b98186a`); current submodule `b264e35`.
    - `forge.toml`: `test_command`, `test_command_full`, `lint_command`, `format_command`, `type_command`, `strict_agent_system = true`.
    - `AGENTS.md`: `/i18n-maintenance` added; `qa-docker` migrated to `testing-standards` (deprecated upstream alias); `[project]` command keys documented.
    - `.agent-state/next_steps.md` and `task.md` updated; next-steps snapshot archived for 2026-10-19; metrics synced and session rotated.
- **Quality**: 233/233 tests; `ruff check` + `mypy src/` clean; framework `validate` (18 skills / 14 workflows / 3 templates), `--graph`, `--conflicts`, `metrics validate` (38 files), `memory check` (169/350) and framework tests (37) green.
- **Maintenance**: [session_2026-10-19_agentic_forge_v1.4.2.md](maintenance/session_2026-10-19_agentic_forge_v1.4.2.md)

## [2026-10-11] Incremental Cache & Unified Rule Registry (v1.16.0)
- **Added**: incremental per-file analysis cache (`--no-cache` to disable) with real invalidation (analyzer version + source fingerprint + resolved project path + effective config); deterministic, path-sorted output.
- **Added**: unified rule registry (`src/analyzer/rules/`) as the single source of truth for all **51** rules; `list-rules` now covers every rule (+ `--format text|markdown`); `RULES.md` is generated by `scripts/generate_rules_md.py` and drift-guarded by tests.
- **Changed**: emitted severity follows the catalog (per-rule) instead of always `medium`; `MISSING_I18N` gated for `generic` projects; `security` applies config overrides; `complexity_refactoring` priority `medium`. Modules over 400 lines split.
- **Quality**: 233 tests; `ruff check` + `mypy src/` clean; self-analysis `--max-cc 15` green; self-run findings 80→10 (all LOW); type hints **100%**, docstrings **100%**; maintainability 99.9; security 100.

## [2026-10-11] B102/B307 False-Positive Fix (v1.15.2)
- **Fixed**: `check_exec_eval` matched attribute calls (callee *name*), so `QDialog.exec()` / `self.dlg.exec()` / `table.eval()` were reported as builtin arbitrary code execution. It now flags only bare-name `exec(...)`/`eval(...)`; attribute/method calls are ignored. Two regression tests added.
- **Notes**: no rule-id, CLI or output-contract changes; drop-in patch.
- **Quality**: ruff + mypy clean · 194 tests (coverage 86%) · self-analysis `--max-cc 15` green.

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
