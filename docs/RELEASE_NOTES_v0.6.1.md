# Release Notes - v0.6.1 (2025-12-31)

This patch release fixes a critical issue with the `.analyzerignore` logic where certain scanners were not respecting the ignore rules, and improves the overall pattern matching to be more intuitive.

## What's New

### 🏗 Architectural Refactorings
- **Multi-processing Engine**: Analysis is now powered by `ProcessPoolExecutor`, making it up to 4x faster on multi-core systems.
- **Project Auto-Detection**: The analyzer now automatically detects if a directory is a `Generic Python Project` or a `QGIS Plugin`, adjusting the compliance requirements and scoring rules dynamically.
- **UI/UX Enhancements**: New progress bar with ETA and improved terminal logging.

### 🛠 Fixes & Improvements
- **Robust `.analyzerignore` Engine**: 
  - Pattern matching now supports non-anchored directories (e.g., `dist/` will match at any depth).
  - Added support for anchored patterns (patterns starting with `/`).
- **Universal Privacy**: 
  - Fixed a regression where the Binary Scanner and Package Size Calculator were ignoring `.analyzerignore` rules.
  - No more false positives from `.venv` or temporary build folders in your quality score!
- **Default Excludes**: 
  - Built-in protection for common development folders: `.venv`, `venv`, `__pycache__`, `.git`, `.github`, `build`, `dist`.
  - These folders are now automatically excluded from all scanning phases even if not explicitly listed in `.analyzerignore`.

## Performance
- By correctly skipping environment and build directories, the analysis phase for projects with large virtual environments is now significantly faster and more accurate.

---
*QGIS Plugin Analyzer - Keeping your PyQGIS code clean and compliant.*
