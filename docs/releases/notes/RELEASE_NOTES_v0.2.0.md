# Release Notes - v0.2.0 🛡️

We are pleased to announce the release of **QGIS Plugin Analyzer v0.2.0**. This update focuses on giving developers more control over the analysis process and improving the project's professional presentation.

## 🚀 Key Features

### 🛡️ Selective Auditing with `.analyzerignore`
You can now exclude specific files or directories from being scanned by the analyzer. This is useful for ignoring third-party libraries, generated resources, or development environments.
- Supports standard glob patterns (e.g., `vendor/`, `*.pyc`).
- Implementation is entirely dependency-free, using Python's native `fnmatch` module.

## 💎 Enhancements

### 🔝 Professional Header & Badges
The `README.md` has been upgraded with professional status badges:
- **Project Version**: Tracks the latest release.
- **Python Compatibility**: Clearly shows Python 3.8+ support.
- **License**: Confirms GPL-v3.0+ compliance.
- **Conventional Commits**: Highlights our commitment to structured development.

## 🛠️ Internal Improvements
- Optimized file discovery logic in `ProjectAnalyzer`.
- Improved error handling for missing imports in the core engine.
- Cleaned up temporary test artifacts to maintain a lean repository.

## 📦 How to Update
If you installed the analyzer using `uv`:
```bash
uv tool upgrade qgis-plugin-analyzer
```
Or for local development:
```bash
git pull origin main
uv sync
```

---
*Thank you for being part of the QGIS community!*
