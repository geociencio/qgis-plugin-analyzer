# Release Notes: v1.2.0 - The Integration Release

**Version:** 1.2.0
**Date:** 2026-01-02
**Title:** The Integration Release

This release transforms `qgis-plugin-analyzer` from a standalone CLI tool into a fully integrated ecosystem component. It introduces native support for **GitHub Actions** and **Pre-commit Hooks**, making it easier than ever to maintain plugin quality automatically.

## 🌟 Key Features

### 🔌 Native GitHub Action
You can now use the analyzer directly in your GitHub Actions workflows without manual installation steps.
```yaml
- uses: geociencio/qgis-plugin-analyzer@v1.2.0
  with:
    path: .
```

### 🔄 Pre-commit Hook
Run checks automatically before every commit by adding this to your `.pre-commit-config.yaml`:
```yaml
- repo: https://github.com/geociencio/qgis-plugin-analyzer
  rev: v1.2.0
  hooks:
    - id: qgis-plugin-analyzer
```

### 📦 PyPI Standardization
The project metadata has been overhauled to meet 2025 PyPI standards, ensuring better discoverability and compatibility with modern package managers like `uv`.

## 📋 Full Changelog
**Added**
- Native `action.yml` for GitHub Actions support.
- Native `.pre-commit-hooks.yaml` for pre-commit support.
- Enhanced `pyproject.toml` metadata (Classifiers, URLs, Authors).

**Fixed**
- None.

**Removed**
- None.
