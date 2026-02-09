# Remaining Issues & Technical Debt

This document tracks resolved and outstanding issues in the **QGIS Plugin Analyzer**.

## ✅ Resolved in v1.7.0
- **SSRF Protection**: Implemented `is_ssrf_safe` validation in `validators.py` to block access to private/loopback IP ranges during metadata URL checks.
- **XXE Mitigation**: Standardized on `xml.etree.ElementTree` for resource scanning, which is safe from external entity injection by default in Python 3.
- **Engine Performance**: Optimized AST traversal to a single-pass model and implemented shared worker context to avoid redundant data serialization.
- **Rule Documentation**: Comprehensive update to `RULES.md` and `README.md` covering all 1.7.0 features (Safety, Performance, CLI).
- **Test Coverage**: Expanded test suite to cover security vulnerabilities and new safety audits.

## 🚧 Outstanding Issues

### 1. Broad Exception Handling
**File**: `src/analyzer/cli/base.py` and `src/analyzer/scanner.py`
**Issue**: Several locations still use broad `except Exception` blocks that could mask specific recovery opportunities or debugging information.
**Recommendation**: Carry out a targeted refactor to use specific exception types (e.g., `pathlib.Path.relative_to` errors, `urllib` errors).

### 2. Path Traversal Guardrails
**Issue**: While many paths are handled via `pathlib`, some operations could benefit from explicit "jail" validation to ensure analysis never escapes the project root.
**Recommendation**: Implement a `path_utils.is_within_root()` check for all file-reading operations.

### 3. Advanced Input Validation
**Issue**: Configuration values in `pyproject.toml` (like rule levels) are assumed to be strings.
**Recommendation**: Add a validation layer in `config_utils.py` to ensure profile settings are well-formed before starting the engine.

### 4. Interactive UI for HTML Reports
**Issue**: The current HTML report is static.
**Recommendation**: Integrate a lightweight JS library (or vanilla JS) for sortable tables and collapsible find sections within the dashboard.

---
*Last updated: 2026-02-09*