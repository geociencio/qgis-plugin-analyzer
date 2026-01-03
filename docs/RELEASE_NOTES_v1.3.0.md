# Release v1.3.0: The "Reliability & Experience" Update

We are proud to announce **QGIS Plugin Analyzer v1.3.0**! This release significantly matures the development ecosystem by introducing strict type checking and optimizing the CLI experience for professional workflows.

## 🚀 Key Highlights

### 🛡️ Type Checking (Mypy Integration)
The analyzer now officially supports and enforces static type checking.
- **`mypy` & `qgis-stubs`**: We've added native support for PyQGIS type stubs.
- **Strict Baseline**: The project itself now passes strict type checks (100% clean baseline).
- **Verification**: Added `uv run mypy .` to the contribution verification steps.

### 💻 Optimized CLI Experience
We've inverted the output defaults to align with standard linter behaviors (like Ruff or Pylint).
- **Default (Screen-Only)**: `qgis-analyzer analyze .` now outputs a concise terminal summary by default. No more cluttering your workspace with report folders unless you ask for them.
- **Reporting Mode**: Use the new `-r` or `--report` flag to generate the full HTML dashboard and Markdown summaries.
  ```bash
  qgis-analyzer analyze . --report
  ```

## 📋 Full Changelog
### Added
- **Type Checking**: Full integration with `mypy` and `qgis-stubs`.
- **CLI**: Added `--report` flag. Changed default output to screen-only.

## 📦 Installation / Upgrade
```bash
pip install --upgrade qgis-plugin-analyzer
# or
uv add qgis-plugin-analyzer
```
