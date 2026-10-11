# Session 2026-10-10 — Deep-Analysis Backlog & Security Restore (v1.15.1)

**Topic**: `deep_analysis_security_v1.15.1`
**Input**: `docs/reports/DEEP_ANALYSIS_v1.15.0_DEAD_CODE_DUPLICATION.md`

## Summary

Executed the full prioritized backlog from the deep-analysis report, then shipped
**v1.15.1** (patch) and deep-updated the README.

## Delivered

| Priority | Change | Commit |
| :--- | :--- | :--- |
| **P0** | Restored the Bandit-inspired security registry (was never imported → all AST security checks disabled; also affected `qgis-plugin-manager`) + regression test | `4f42f59` |
| **P1** | `SCOPE_RULES` single source of truth; reuse `I18N_METHODS`; removed dead `models/`, `modernization_rules`, unused helpers | `2d6f48a` |
| **P2** | CC cut (`run` 16→1, `visit_For` 18→1, `visit_Constant` 17→8); removed unused validator helpers | `5c4f728` |
| **P3** | Coverage 75%→86% (graph 100%, serve 89%, fixer 81%, summary 93%); CI floor 80 | `8e0da56` |
| Docs | Deep-updated README; comparison moved to `docs/research/COMPARISON_VS_ALTERNATIVES.md` | `ad50514` |
| Release | **v1.15.1** prepared, tagged, pushed, GitHub Release with artifacts | `27dc589` |
| Follow-up | **v1.15.2** (maintainer): fixed `B102`/`B307` false positives on `QDialog.exec()`/attribute calls; docs/CI release-process guides | `d91af59`, `c3f5920`, `738d8ec`, `703e2f7`, `2a3550c` |

## Report corrections (hallucination hunt)

- `transformers.apply_transformation` is **not** dead (used by `tests/test_fixer.py`) → kept.
- Pattern/anti-pattern sources were already deleted upstream (only `.pyc` remained) → the port was from scratch.

## Verification

- `ruff` + `format` + `mypy` clean · **194 tests** (incl. 2 attribute-call regressions) · coverage **86%** · self-gate `--max-cc 15` green.
- Self-run: quality 54.5 / maintainability 86.7 / security 100.
- `python -m build` + `twine check` PASSED; GitHub Releases `v1.15.1` and `v1.15.2` created. Latest released version: **1.15.2**.

## Follow-ups (deferred)

- **PyPI upload of v1.15.1** — manual (maintainer): `uv publish --token <TOKEN>`.
- **Module splits** (`engine`/`fixer`/`summary_reporter` > 400 lines) — cosmetic, medium risk; deferred by agreement.
- **Fase 6** unified rule registry to auto-generate `RULES.md`.
- Fase 2.2 incremental cache (`--no-cache`).

## Cross-tool

- Restoring the security registry also fixes the `qgis-plugin-manager` inherited
  false negative (`qgis-manage security` delegates to `qgis-analyzer security`).
