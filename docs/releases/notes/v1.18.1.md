# v1.18.1: Distribution Boundary Fix 📦

Patch release. No analyzer behavior changes: this fixes the wheel/sdist contents so
distributions contain only the tool source and the metadata required to install it.

## Fixed

- **Wheel boundary**: explicit setuptools src-layout discovery
  (`package-dir = {"" = "src"}`, `include = ["analyzer*"]`,
  `include-package-data = false`). The wheel no longer ships a top-level
  `__init__.py`; `top_level.txt` is now only `analyzer`.
- **Sdist boundary**: `MANIFEST.in` prunes `tests/`, `docs/`, `scripts/`, `.agent/`,
  `.agent-state/`, analysis results, caches and generated `egg-info` inside `src/`.
  The sdist contains only `src/analyzer/*.py` plus standard install metadata
  (`LICENSE`, `README.md`, `pyproject.toml`, `MANIFEST.in`, `PKG-INFO`, `setup.cfg`
  and the setuptools `SOURCES.txt`).
- Added `tests/test_packaging.py` guards so the boundary cannot silently regress.

## Upgrade

```bash
pip install --upgrade qgis-plugin-analyzer
```

or, with optional portal tools:

```bash
pip install --upgrade "qgis-plugin-analyzer[portal]"
```

## Verification

- Wheel: 83 files, all `analyzer/*` + `.dist-info`; no tests/docs/root `__init__.py`.
- Sdist: no `tests/`, `docs/`, `scripts/`, agent state or generated reports.
- Wheel and sdist installed in fresh virtual environments; `qgis-analyzer --version`
  reports `1.18.1` in both.
- `twine check` PASSED for the wheel and sdist.

## Quality

- **285 tests**, 89.33% coverage; `ruff check` + `mypy src/` clean.
- Self-analysis `--max-cc 15` green with 10 LOW findings.
- Module Stability 54.0 · Maintainability 99.9 · Security 100.0.
