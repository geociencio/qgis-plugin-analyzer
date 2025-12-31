# Competitive Analysis: QGIS Plugin Tools 🛡️

This document compares `qgis-plugin-analyzer` with existing tools in the ecosystem to identify opportunities for improvement and differentiation.

## 1. Tool Comparison

| Feature | **QGIS Plugin Analyzer** | **flake8-qgis** | **qgis-plugin-ci** | **Official Repo Checks** |
| :--- | :---: | :---: | :---: | :---: |
| **Static Linting** | ✅ (Ruff + AST + Regex) | ✅ (Flake8) | ❌ | ❌ |
| **QGIS Best Practices** | ✅ (Comprehensive) | ✅ (Limited `QGS101-106`) | ❌ | ✅ (Manual/Basic) |
| **CI/CD Lifecycle** | ❌ (Integration ready) | ❌ | ✅ (Build/Release) | ❌ |
| **Metadata Validation** | ✅ (Structure & Fields) | ❌ | ❌ | ✅ (Repository side) |
| **Architecture Audit** | ✅ (Logic in UI detection) | ❌ | ❌ | ❌ |
| **Speed** | 🚀 (Parallel + Rust) | 🐢 (Single thread) | N/A | N/A |

## 2. Key Findings & Opportunities

### A. vs `flake8-qgis`
**Status**: We cover most of their rules (`qgis._core`, `gdal` import, `QgisInterface`).
**Gap**: We may miss some specific PyQt direct import checks (`QGS103`, `QGS104`).
**Action**:
- Ensure strict parity with `QGS1xx` rules so users can fully replace `flake8-qgis`.
- Create a "Migration Guide" showing how to map internal IDs to `QGS` codes.

### B. vs `qgis-plugin-ci`
**Status**: This tool focuses on *process* (release, transifex), while we focus on *code quality*.
**Gap**: We don't verify if translations are actually *present*, only if code is *translatable*.
**Action**:
- **Translation Integrity**: Check if string keys in code actually match entries in `.ts` files.
- **CI Generator**: Add ability to generate `.github/workflows` that install and run both `qgis-plugin-ci` (for release) and `qgis-plugin-analyzer` (for quality).

### C. vs Official Repository Checks
**Status**: The official repo rejects plugins with binaries or broken metadata links.
**Gap**: We currently don't check for binary files or valid URLs.
**Action**:
- **Binary Scanner**: Fail if `.dll`, `.exe`, `.so`, `.dylib` files are found.
- **Link Validator**: (Optional) Check if `metadata.txt` URLs (homepage, tracker) return 200 OK.

## 3. Recommended Advancements

Based on this analysis, the following features should be added to the Roadmap:

### 1. "Repository Compliance" Suite
Expand the current metadata check to a full compliance suite that mimics the official QGIS Plugin Repository validation logic locally.
- **No Binaries**: Recursive scan for prohibited binary extensions.
- **Size Check**: Warn if plugin exceeds recommended size (e.g., 20MB).
- **Link Rot**: Validate HTTP links in metadata.

### 2. Flake8-QGIS Parity Mode
Add a specific profile or reporting mode that maps our findings to `QGS` codes, making migration easier for existing teams.

### 3. CI Integration Helper
Since we removed the project generator, we can add a small helper to generate just the CI configuration:
```bash
qgis-analyzer ci-wizard
```
This would create a `.github/workflows/audit.yml` file.
