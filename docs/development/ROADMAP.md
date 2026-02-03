# Roadmap: QGIS Plugin Analyzer 🚀

This document outlines the strategic improvements and technical advancements planned for the next phases of `qgis-plugin-analyzer`.

## 1. 🛠️ PyQGIS specific Audits (Code Quality)

| Feature | Description | Priority |
| :--- | :--- | :--- |
| **Qt Shim Enforcement** | Detect direct `PyQt` or `PySide` imports and suggest `qgis.PyQt`. | High |
| **Unload Verification** | Ensure every plugin implements a proper `unload()` method for cleanup. | High |
| **API Modernization** | Detect deprecated methods (e.g., `writeAsVectorFormat`) and suggest new ones. | Medium |
| **Internal API Audit** | Warn against using `qgis._core` or other protected/internal members. | High |

## 2. ⚡ Performance Optimization

- **Spatial Filter Audit**: Warn when iterating `getFeatures()` on large layers without spatial or attribute filters.
- **Main Thread Guardians**: Detect blocking operations (network, heavy processing) being called from the main GUI thread.
- **Task Verification**: Ensure `QgsTask` is used correctly for long-running operations.

## 3. 🌍 Internationalization (i18n)

- **Translation Check**: Verify that all user-visible strings are wrapped in `self.tr()` or `QCoreApplication.translate()`.
- **TS File Sync**: Automated checking of `.ts` files to ensure they are up to date with the code.

## 4. 🎨 UI/UX Consistency

- **Widget Standard**: Detect standard Qt widgets and suggest QGIS custom widgets (e.g., `QgsFileWidget`, `QgsMapLayerComboBox`) for a native look.
- **Icon Quality**: Validate that plugin icons meet size and format requirements for the official repository.

## 5. 📦 Packaging & Metadata

- **Dependency Analysis**: Audit the `metadata.txt` description and category against official QGIS tags.
- **Broken Link Checker**: Automatically verify that URLs in `metadata.txt` (homepage, tracker) are not 404.
- **Automated Versioning**: Command to safely bump versions across `metadata.txt` and `pyproject.toml`.

## 6. 👨‍💻 Developer Experience (DevX)

- **Scaffolding**: `init` command enhancement to generate boilerplate for specific QGIS components (Processing providers, Custom Widgets).
- **QGIS Documentation Integration**: Linking detected errors directly to the official PyQGIS documentation.

## 7. Infrastructure & Integration (Pending)

- **GitHub Actions**: Create a dedicated GitHub Action in the marketplace that uses this tool.
- **Pre-commit Hook**: Official support for `.pre-commit-config.yaml`.
- **Type Checking Pipeline**: Fully integrate `mypy` execution into the report pipeline (beyond just local development checks).
