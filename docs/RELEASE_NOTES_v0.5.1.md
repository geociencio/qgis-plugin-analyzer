# Release Notes - v0.5.1 (Refinement & Stability) 🚀

This release focuses on improving the stability, consistency, and performance of the QGIS Plugin Analyzer after the major 0.5.0 features. We've addressed critical bugs identifies in our internal audit and streamlined the validation architecture.

## 🚀 What's New

### 🛠️ Architecture & Refactoring
- **Consolidated Validators**: The logic for checking plugin structure and metadata has been centralized into `src/analyzer/validators.py` for better maintainability.
- **Improved TOML Parser**: Enhanced the built-in minimal TOML parser to handle numeric values and quoted strings more robustly, ensuring better profile loading.

### 🐞 Bug Fixes
- **Consistent Rule IDs**: Unified rule identifiers (e.g., `UNPRECISE_LAYER`, `MANUAL_RESOURCE_PATH`) across AST and Regex audits to ensure consistent reporting and log correlation.
- **Engine Stability**: Fixed an `AttributeError` involving the ignore matcher and corrected function signatures in the parallel processing worker.
- **Missing Imports**: Added missing dependencies in `fixer.py` and `semantic.py` for tempfile handling and XML parsing.
- **Correct Metadata Path**: Fixed a discrepancy in how `metadata.txt` was being located during full project analysis.

### ⚙️ CLI Improvements
- **Profile-aware Fixes**: The `fix` command now accepts the `-p/--profile` argument. This allows the auto-fix engine to respect your custom rule configurations (skipped or severity-adjusted rules) from `pyproject.toml`.

### ⚡ Performance
- **Regex Pre-compilation**: Audit rules based on regular expressions are now pre-compiled, providing a performance boost when analyzing large projects with many Python files.

## 🧪 Verification
- All 24 core unit tests are passing.
- Verified configuration-based rule filtering with new regression test cases.

## 📦 How to update
If you are using `uv`:
```bash
uv sync
```
Or just pull the latest changes from the repository.

---
*Developed with ❤️ for the QGIS Community.*
