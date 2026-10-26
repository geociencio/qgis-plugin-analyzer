# v1.18.0: Ignore-aware Analysis 🔍

Minor release. Project discovery now honors the repository's ignore files, excludes
documentation and test trees by default, and exposes explicit `--exclude` / `--scope`
controls. This keeps analysis focused on plugin code (and stops `docs/`/`tests/` from
inflating the source-tree size).

## Added

- **Ignore-file awareness**: `.gitignore`, `.qgisignore` and `.analyzerignore` are
  merged with the built-in defaults and evaluated in order. The **last matching
  pattern wins**, with gitignore-style `!pattern` negation.
- **`--exclude PATTERN`** on `analyze`, `security` and `fix`: repeatable or
  comma-separated, with `!` to re-include. Profiles accept an `exclude` list too.
- **`--scope`** on `analyze` (`all`, `i18n`, `security`, `performance`,
  `architecture`, `metadata`), while `analyze [scope] [path]` keeps working.

## Changed

- **Default excludes now include `docs/` and `tests/`** (alongside `.venv/`,
  `build/`, `dist/`, caches and generated artifacts). Analysis, source-tree size,
  scoring, Ruff/Flake8 and external security findings all use the same matcher.
- Re-include a default exclusion with a negation:

  ```bash
  qgis-analyzer analyze . --exclude '!docs/'
  qgis-analyzer analyze . --exclude '!tests/'
  ```

- External security/lint findings from `docs/`, `tests/`, `.venv/` or `build/` are
  filtered out of `security --json` and `analyze --json`; they no longer leak into
  reports even though the tools scan the tree themselves.
- The profile `exclude` list participates in the same precedence:
  defaults → `.gitignore` → `.qgisignore` → `.analyzerignore` → profile/CLI.

## Notes

- The matcher covers the practical gitignore subset: anchored `/foo`, directory
  `build/`, basename `*.pyc`, basic `**` globs and `!` negation. Nested
  `.gitignore` files are not loaded.
- `fix` now respects the defaults too, so it will not rewrite `docs/` or `tests/`
  unless they are explicitly re-included.
- This is a behavior change for projects that previously expected `docs/`/`tests/`
  to be analyzed; use `--exclude '!docs/'` (or a `!docs/` rule) to restore the old
  scope.

## Upgrade

```bash
pip install --upgrade qgis-plugin-analyzer
```

Typical commands:

```bash
qgis-analyzer analyze . --scope i18n
qgis-analyzer analyze . --exclude '!docs/' --exclude '!tests/'
qgis-analyzer security . --exclude 'generated/'
qgis-analyzer fix . --exclude '!tests/fixtures/'
```

## Quality

- **283 tests**, 89.33% coverage; `ruff check` + `mypy src/` clean.
- Self-analysis `--max-cc 15` green with 10 LOW findings.
- Rule catalog: **56** rules; Module Stability 54.0 · Maintainability 99.9 ·
  Security 100.0.
