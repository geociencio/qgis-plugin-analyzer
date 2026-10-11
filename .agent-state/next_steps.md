# Next Steps — Handover (2026-10-11, v1.15.2 released)

## Session Summary (topic `deep_analysis_security_v1.15.1`)

Executed the full deep-analysis backlog
(`docs/reports/DEEP_ANALYSIS_v1.15.0_DEAD_CODE_DUPLICATION.md`) and shipped
**v1.15.1** (patch): restored the disconnected security registry, removed dead
code, cut complexity, raised coverage 75%→86%, deep-updated the README.
The maintainer then released **v1.15.2** (fixes `B102`/`B307` false positives
on `QDialog.exec()`/attribute calls) plus release-process/agentic docs.

### Completed
- [x] **P0** Security registry restored (`security_rules` imported for its registration side effect) + regression test.
- [x] **P1** `rules/scopes.py` single source of truth; reuse `I18N_METHODS`; removed `models/`, `modernization_rules`, unused helpers.
- [x] **P2** CC cut: `run` 16→1, `visit_For` 18→1, `visit_Constant` 17→8.
- [x] **P3** Coverage 75%→86%; CI coverage floor 80; 194 tests.
- [x] README deep update; comparison moved to `docs/research/COMPARISON_VS_ALTERNATIVES.md`.
- [x] **v1.15.1** and **v1.15.2** released on GitHub (artifacts; `twine check` PASSED).

## How to Resume
1. Run `/start-session`.
2. ~~If continuing the release: upload the latest version to PyPI (manual).~~ **DONE** — `1.15.2` (wheel + sdist) is live on PyPI (uploaded 2026-10-11T01:27Z by CI `publish-pypi`).

## Remaining / Next
- [x] ~~**PyPI upload** of the latest release~~ — complete (verified on PyPI).
- [x] ~~Module splits (`engine`/`fixer`/`summary_reporter` > 400 lines)~~ — done; also `commands.py`. All src modules ≤ 400 lines (`docs/plans/implementation_plan_module_splits.md`).
- [x] ~~**Fase 6** unified rule registry to auto-generate `RULES.md`~~ — done; `list-rules` + `RULES.md` now cover all 51 rules (`docs/plans/implementation_plan_rule_registry.md`).
- [x] ~~Fase 2.2 incremental cache (content hash) + `--no-cache`~~ — done (`docs/plans/implementation_plan_incremental_cache.md`).
- [ ] Tune anti-pattern noise (`MAGIC_NUMBER`×35, `SPAGHETTI_CODE`×10 on self-run).

## 🐛 Known Issues

**None blocking** — 232 tests passing; `ruff check` + `mypy src/` clean; self-analysis `--max-cc 15` green (max func CC 13).

- **Metrics validator false positives**: `forge.py metrics validate` flags **5**
  entries in the `.agent/` framework submodule — `scaffold/qgis/workflows/release-plugin.md`
  (CC ≤ 10 ×3, 763 tests → the SecInterp domain template) and `skills/coding-standards/SKILL.md`
  ("complexity below 10" → generic guideline). These are template/domain values, not
  stale analyzer metrics (CC ≤ 15, 232 tests). The validator scans `scaffold/` against
  this project's ground truth; treat as non-blocking until the framework excludes
  domain packs from ground-truth checks. Disposition mirrors `ai-context-core`
  (see `AGENT_LESSONS.md` 2026-10-11). Do **not** patch the submodule or lower `max_cc`.
  (The count rose 4→5 once `agent_metrics.json` gained a ground-truth `summary`, so the
  scaffold's "763 tests" is now also compared.)

## Technical Debt
- [ ] Self-reported `MISSING_I18N` in the analyzer's own codebase.
- [ ] Coverage at 86% (floor 80%) — keep incremental gains.

## Watch-outs
- Keep the `project_context.json` schema keys stable (consumed by `ai-context-core`; bump `schema_version` on change).
- Keep CLI subcommands/flags stable (consumed by `qgis-plugin-manager`).
- Security rules: verify a registry populated by import side effects stays non-empty (see AGENT_LESSONS 2026-10-10).
