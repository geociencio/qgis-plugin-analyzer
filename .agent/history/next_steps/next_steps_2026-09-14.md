# Next Steps — Phase: Analyzer Generalization (Handover 2026-09-14)

## Session Summary (2026-09-14)

Analyzed the upstreaming plan (`docs/plans/`) against the current codebase and
implemented **Fase 0 (CI output contract)** of the analyzer generalization effort.
Created the 5-phase implementation plan document.

### Completed This Session
- [x] Analyzed `docs/plans/upstreaming_qgis_analyzer.md` + `i18n_ast_rule.py`
- [x] Created `docs/plans/implementation_plan_generalize_analyzer.md`
- [x] Fase 0.1: `schema_version` + `analyzer_version` in `project_context.json`
- [x] Fase 0.2: `--include-content` flag (module source omitted by default)
- [x] Fase 0.3: `--json` flag (pure JSON on stdout; logs/progress routed to stderr)
- [x] Fase 0.4: legacy `json/project_context.json` migration warning
- [x] Commits: `7a969ad` (feat), `a8cfd50` (docs)

### Remaining for Next Session
- [ ] Fase 1: port i18n AST rule into `I18nVisitor` (replace `is_translatable_string`)
- [ ] Fase 2: `--max-cc N` complexity gate
- [ ] Fase 3: bump `requires-python >= 3.11` + remove `_minimal_toml_load`
- [ ] Fase 4: tests (SecInterp golden corpus, synthetic fixtures, CC gate, back-compat)
- [ ] Fase 5: reconcile `docs/qgis-analyzer-i18n-improvement.md`

### Technical Debt
- [ ] Reduce 570 self-reported MISSING_I18N in analyzer's own codebase
- [ ] Address 2 HIGH_COMPLEXITY issues in `ast_utils.py`
- [ ] Fix setuptools deprecation warnings (license format in `pyproject.toml`)

## How to Resume
1. Run `/start-session`
2. Relocate reference: `git mv docs/plans/i18n_ast_rule.py scripts/upstream/i18n_ast_rule.py`
3. Implement Fase 1 (port `I18nAstVisitor` + `collect_docstring_lines` + `is_technical_string` to `visitors/i18n_visitor.py`)
