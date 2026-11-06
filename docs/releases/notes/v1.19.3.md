# v1.19.3: Canonical CLI Entry Point 🧭

Patch release. Consolidates the CLI entry point and adds the standard
`python -m analyzer` invocation. No command behavior changed.

## Changed

- **Single canonical entry point**: `analyzer.main:main`. `pyproject.toml` still
  installs `qgis-analyzer` with that target.
- **`analyzer.cli` is now a pure re-export** of `CLIApp`; the duplicated
  `analyzer.cli.main` implementation was removed.
- `CLIApp`, its command discovery and `CLIApp.run()` are unchanged.

## Added

- **`python -m analyzer`** is now supported through `src/analyzer/__main__.py`.
  `python -m analyzer.main` and the `qgis-analyzer` script keep working.

## Removed

- `from analyzer.cli import main` no longer resolves. Use
  `from analyzer.main import main` or the installed `qgis-analyzer` script.

## Verification

```bash
qgis-analyzer --version       # qgis-analyzer 1.19.3
python -m analyzer --version  # __main__.py 1.19.3
python -m analyzer.main --version
```

## Upgrade

```bash
pip install --upgrade qgis-plugin-analyzer
```

## Quality

- **318 tests**, 89.5% coverage; `ruff check` + `mypy src/` clean.
- Self-analysis `--max-cc 15` green with 10 LOW findings.
- Rule catalog: **56** rules; Module Stability 53.9 · Maintainability 99.9 ·
  Security 100.0.
