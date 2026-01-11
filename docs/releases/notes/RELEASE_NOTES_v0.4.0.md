# Release Notes - v0.4.0 🚀

This release marks a major architectural milestone for the **QGIS Plugin Analyzer**. We have achieved **Zero Runtime Dependencies** while maintaining 100% functionality and a professional reporting system.

## 📦 What's New in v0.4.0?

### 🛡️ Zero Runtime Dependencies
The analyzer no longer requires any external Python packages to function.
- **Native TOML Support**: Replaced `tomli` with a custom-built, lightweight TOML extractor optimized for QGIS plugin profiles.
- **Manual HTML Reporting**: Replaced `dominate` with a high-performance, template-free HTML generator that preserves our professional design system.

### 🧪 Standard Test Suite
We have migrated our entire testing infrastructure from `pytest` to the native Python `unittest` framework.
- **Improved Portability**: Tests can now be run in any environment with just `python3 -m unittest`.
- **Cleaner Stack**: Removed `pytest` from development dependencies, further reducing the project's footprint.

### ⚡ Performance & Efficiency
- **Faster Startup**: By removing external library imports, the analyzer starts and executes even faster.
- **AI-Native Refactors**: The codebase is now even cleaner and more accessible for AI assistants and automated audits.

## 🛠️ Installation Update

Since the project no longer has external runtime requirements, installation is now purely a matter of cloning or piping:

```bash
# Global installation with uv
uv tool install git+https://github.com/geociencio/qgis-plugin-analyzer.git

# No more 'pip install' dependency resolving!
```

---
*Empowering the QGIS community with lightweight, professional tools.*
