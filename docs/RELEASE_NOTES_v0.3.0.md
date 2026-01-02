# Release Notes v0.3.0: The Quality Leap 🚀

We are proud to announce the release of **QGIS Plugin Analyzer v0.3.0**. This version represents a massive upgrade in terms of precision, performance, and developer experience, moving away from simple regex checks to a powerful Abstract Syntax Tree (AST) engine.

## 🌟 New Features

### 1. Unified Linting with Ruff
We've integrated **Ruff**, the fastest Python linter, directly into our workflow. Now you get the best of both worlds:
- Standard Python best practices (PEP8, unused imports, etc.) powered by Ruff.
- Specialized QGIS audits powered by our custom engine.

### 2. Deep AST Audit Engine
Most critical rules have been migrated to **AST (Abstract Syntax Tree)** analysis. This means:
- **Zero false positives** from comments or multi-line strings.
- **Context-aware detection** of missing translations and obsolete APIs.

### 3. Professional Boilerplate Generation (`init`)
Start your next plugin correctly in seconds! Use the new `init` command:
- `qgis-analyzer init my_plugin --type processing`: For algorithmic power.
- `qgis-analyzer init my_plugin --type gui`: For interactive tools with menubar/toolbar.
- `qgis-analyzer init my_plugin --type map_tool`: For advanced map interaction.

### 4. Advanced Configuration Profiles
Take control of your CI/CD pipeline with profiles in `pyproject.toml`:
- **Default Profile**: Friendly for development.
- **Release Profile**: Strict mode enabled! Fails the build if QGIS compliance isn't 100%.

### 5. Stunning HTML Reports
Get a visual overview of your project's health with professional HTML reports, including quality scores and categorized findings.

## 🛠️ New Audit Rules (Inspired by flake8-qgis)

- **`QGS101/102` (Protected Members)**: Flags imports from `qgis._core/gui`.
- **`QGS105` (Iface as Argument)**: Discourages passing `QgisInterface` to maintain clean architecture.
- **`QGS106` (GDAL Imports)**: Encourages the use of `osgeo.gdal`.
- **`MANDATORY_CLEANUP`**: Ensures `unload()` is present if `initGui()` is used (prevents memory leaks).

## 🐛 Bug Fixes & Stability
- Improved handling of syntax errors during analysis.
- Stabilized core utility modules and optimized parallel processing.
- Renamed internal templates to `.tmpl` to keep your IDE clean.

## 🚀 Get Started

Update or install using `uv`:
```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-analyzer.git
```

Run your first professional audit:
```bash
qgis-analyzer analyze . --profile release
```

---
*Helping the QGIS community build better, robust, and AI-ready plugins.*
