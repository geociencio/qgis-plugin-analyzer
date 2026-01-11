# Release Notes - v0.5.0 🚀

This release introduces the most powerful analysis features yet for the **QGIS Plugin Analyzer**. Version 0.5.0 focuses on **Deep Semantic Analysis**, **Interactive Auto-Fixes**, and **Official Repository Compliance**, making it the ultimate tool for PyQGIS developers.

## 📦 What's New in v0.5.0?

### 🧠 Deep Semantic Analysis
Go beyond simple syntax checks with our new semantic engine.
- **Dependency Graphing**: Detect circular imports and visualize module coupling (fan-in/fan-out).
- **Resource Validation**: Automatically cross-reference your Python code with `.qrc` files to find missing or broken resource paths (`:/plugins/...`).
- **Signal/Slot Safety**: Detect `POTENTIAL_MISSING_SLOT` issues before they crash QGIS.

### 🛠️ Interactive Auto-Fix Mode
Save hours of manual refactoring with our new `fix` command.
- **AST-Based Transformers**: Safely transform code structures using our robust transformation engine.
- **Safety First**: Features a mandatory **Git Status Check** and interactive **Diff Preview** before any changes are applied.
- **Smart Fixers**:
    - `GDALImportFixer`: Modernizes GDAL imports.
    - `LegacyImportFixer`: Bridges PyQt4/PyQt5 to `qgis.PyQt`.
    - `PrintToLogFixer`: Converts `print()` to `QgsMessageLog`.
    - `I18nFixer`: Wraps UI strings in `self.tr()`.

### 📦 Repository Compliance Suite
Catch rejection reasons *before* you submit to `plugins.qgis.org`.
- **Binary Scanner**: Proactively warns about prohibited `.exe`, `.dll`, or `.so` files in your package.
- **Size Validation**: Ensures your plugin stays within the 20MB recommended limit.
- **Metadata Link Checker**: Validates that your homepage, tracker, and repository URLs are actually working.

### ⚙️ Enhanced Configuration Profiles
Total control over your analysis standards.
- **Rule-Level Control**: Enable, disable, or change the severity of individual rules in `pyproject.toml`.
- **Custom Severities**: Use `error`, `warning`, `info`, or `ignore` to match your team's workflow.

---

## ⚡ How to get started?

Run the new compliance and fix commands:
```bash
# Full analysis with compliance checks
qgis-analyzer analyze .

# Preview available fixes
qgis-analyzer fix . --dry-run
```

---
*Empowering the QGIS community with lightweight, professional tools.*
