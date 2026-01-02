# 🛡️ QGIS Plugin Analyzer v0.6.1 - The Privacy & Precision Patch

This patch release focuses on fixing critical issues with the `.analyzerignore` engine and ensuring a high-quality analysis experience by introducing **Default Scrutiny Exclusions**.

### 🚀 Key Highlights

- **Universal Ignore Engine**: Fixed a regression where binary scanning and package size calculations were ignoring user-defined `.analyzerignore` rules.
- **Smart Default Excludes**: Automatically skips `.venv`, `__pycache__`, `.git`, and build directories across all analysis phases. 
- **Non-Anchored Patterns**: Improved pattern matching to support intuitive directory ignoring (e.g., `dist/` matches at any depth).
- **Accurate Scoring**: Your Quality Score will no longer be penalized by files inside your virtual environment!

### 📋 Changelog Summary

**Added**
- Default patterns for common development folders (.venv, build, dist, etc.).

**Fixed**
- `.analyzerignore` matching for non-anchored directories.
- Anchored pattern support (starting with `/`).
- Multi-phase ignore enforcement (AST, Binaries, Size).

---
*Helping you build better, cleaner, and AI-optimized QGIS plugins.*
