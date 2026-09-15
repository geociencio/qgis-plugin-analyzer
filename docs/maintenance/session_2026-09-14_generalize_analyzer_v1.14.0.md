# Maintenance Session: 2026-09-14 - Analyzer Generalization & v1.14.0 Release

## Technical Summary

Completed the 5-phase analyzer generalization plan (`implementation_plan_generalize_analyzer.md`),
turning the analyzer into a tool that audits **any** QGIS plugin. Shipped **v1.14.0**
(GitHub + PyPI) with a portable AST-based i18n rule, a `--max-cc` complexity gate,
Qt6 migration rules, and a Python 3.11 floor.

## Changes Made

### Fase 1 — Portable i18n AST rule
- `visitors/i18n_visitor.py` rewritten with the AST rule from
  `scripts/upstream/i18n_ast_rule.py` (relocated in `git mv`).
- Recognizes `self.tr()`/`QCoreApplication.translate()` wrappers, excludes
  docstrings and technical strings, honors inline `# no-i18n`/`# noqa`, and
  supports `extra_ignore_calls`/`extra_exact_ignores` config.
- `scanner.py` threads source lines; `composite_visitor.py` pre-computes
  docstring lines via `collect_docstring_lines`.

### Fase 2 — Cyclomatic complexity gate
- `--max-cc N` flag; `_enforce_max_cc` reports `cc_gate`/`cc_violations` and
  exits 1 on failure.

### Fase 3 — Python 3.11 floor
- `requires-python >=3.11`; removed `_minimal_toml_load` in favor of stdlib
  `tomllib`; type annotations modernized to PEP 585/604.

### Fase 4 & 5 — Tests and docs
- Synthetic i18n tests, CC gate integration tests, back-compat JSON shape.
- Golden SecInterp procedure documented (external corpus).
- `upstreaming_qgis_analyzer.md` reconciled with the `MISSING_I18N` decision.

### Competitive analysis follow-ups
- **Req 1**: `QtTransitionVisitor` with 11 `QT6_*` rules (`QGS4xx` parity).
- **Req 2**: type-hint coverage counts posonly/kwonly/`*args`/`**kwargs`.
- **Req 4 (partial)**: `summary` stale-cache detection via `analyzed_at` +
  `project_path`.
- Setuptools license deprecation resolved (SPDX expression string).

## Verification Results

| Gate | Result |
|------|--------|
| Tests | 126/126 ✅ |
| Ruff | Clean ✅ |
| Mypy | Clean (54 source files) ✅ |
| Build | sdist + wheel OK ✅ |
| `twine check` | PASSED ✅ |
| Self-analysis (strict) | exit 0; Stability 54.8, Maintainability 88.1, Security 100.0 |

## Impact

The analyzer's i18n audit is now AST-precise (no heuristic false positives), the
CI story is complete (`--json`, `--max-cc`, versioned schema), and Qt6 migration
rules provide drop-in parity with `flake8-qgis` `QGS4xx`. Python floor raised to
3.11 (breaking for 3.9/3.10 users, documented in the changelog).

## References
- Plan: `docs/plans/implementation_plan_generalize_analyzer.md`
- Release: `v1.14.0` (GitHub release + PyPI)
- Competitive analysis: `docs/research/COMPETITIVE_ANALYSIS.md`
