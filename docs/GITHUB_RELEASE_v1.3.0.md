# v1.3.0: Reliability & Experience Update

## 🚀 What's New

### 🛡️ Static Type Checking
We have integrated **Mypy** and **qgis-stubs** into the core development workflow. This ensures type safety across the analyzer codebase and provides a robust foundation for future features.

### 💻 Smarter CLI Defaults
The CLI now behaves like a standard linter:
- **Default**: Screen-only summary (perfect for CI/CD logs).
- **With Reports**: Pass `--report` to generate the HTML dashboard.
  ```bash
  qgis-analyzer analyze . --report
  ```

## 📝 Changelog
- **Added**: Native Mypy support with `tool.mypy` configuration.
- **Changed**: `generate_html` defaults to `False`. Reports require `--report`.

**Full Diff**: https://github.com/geociencio/qgis-plugin-analyzer/compare/v1.2.0...v1.3.0
