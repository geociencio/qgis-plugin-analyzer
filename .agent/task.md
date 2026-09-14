# Active Tasks — Phase: Analyzer Generalization (i18n AST + CC gate)

This task board tracks the current development phase based on `.agent/next_steps.md`.
Reference plan: `docs/plans/implementation_plan_generalize_analyzer.md`.

## Goal 1: Analyzer Generalization
- [x] Fase 0.1 — `schema_version` + `analyzer_version` in `project_context.json` <!-- id: 1.1 -->
- [x] Fase 0.2 — `--include-content` flag (content optional) <!-- id: 1.2 -->
- [x] Fase 0.3 — `--json` flag + clean stdout <!-- id: 1.3 -->
- [x] Fase 0.4 — legacy output dir warning <!-- id: 1.4 -->
- [ ] Fase 1 — port i18n AST rule to `I18nVisitor` (replace heuristic) <!-- id: 1.5 -->
- [ ] Fase 2 — CC gate `--max-cc N` <!-- id: 1.6 -->
- [ ] Fase 3 — bump Python >=3.11 + remove `_minimal_toml_load` <!-- id: 1.7 -->
- [ ] Fase 4 — tests (golden, synthetic, CC gate, back-compat) <!-- id: 1.8 -->
- [ ] Fase 5 — docs reconciliation <!-- id: 1.9 -->

## Goal 2: Release Cleanup
- [ ] Upload v1.13.2 to PyPI (manual) <!-- id: 2.1 -->
- [ ] Fix setuptools license deprecation warnings <!-- id: 2.2 -->
- [ ] Add `i18n-standards` and `audit-plugin` triggers to `skill_sync.py` <!-- id: 2.3 -->

## Goal 3: Technical Debt
- [ ] Reduce 570 self-reported MISSING_I18N in analyzer's own codebase <!-- id: 3.1 -->
- [ ] Address 2 HIGH_COMPLEXITY issues in `ast_utils.py` <!-- id: 3.2 -->

## Completed
- [x] I18n fix: `QCoreApplication.translate()` wrapper recognition (v1.13.2)
- [x] Gen 5→6 agentic system upgrade (13 files, 895 insertions)
- [x] v1.13.2 GitHub release
- [x] Fase 0: CI output contract (schema version, `--json`, `--include-content`)

## Operational Status
- **Active Phase**: Analyzer Generalization
- **Current Metrics**:
  - Tests: 87/87 passing (100%)
  - Stability: 55.2/100
  - Maintainability: 77.0/100
  - Security: 100.0/100
