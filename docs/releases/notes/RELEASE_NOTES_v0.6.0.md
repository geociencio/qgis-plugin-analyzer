# Release Notes - v0.6.0 (Security & Performance) 🛡️⚡

This release introduces significant security hardening and architectural optimizations to make the QGIS Plugin Analyzer more robust, safe, and efficient.

## 🛡️ Security Hardening

### SSRF Protection
The URL validation system for `metadata.txt` now includes a protection layer against Server-Side Request Forgery. It resolves hostnames and blocks any IP within private, loopback, or local ranges (e.g., 10.0.0.0/8, 127.0.0.0/8).

### Path Traversal Prevention
All file operations now pass through a safety check (`safe_path_resolve`) that ensures all analyzed paths stay strictly within the project's root directory.

### XML Security
Standardized XML parsing in `ResourceValidator` with built-in safety against External Entity (XXE) attacks.

## ⚡ Performance Optimization

### Intelligent File Caching
The analysis engine now caches file content in memory during the scanning phase. This avoids multiple redundant reads from disk when performing AST analysis followed by regex-based auditing, resulting in faster scans—especially on slow filesystems or networked drives.

## 🔍 Scan Improvements

### Precision Spatial Index Audit
The `SPATIAL_INDEX` rule has been promoted from a regex pattern to a high-precision AST (Abstract Syntax Tree) rule. It can now accurately detect unoptimized `getFeatures()` calls without false positives from similar strings in comments or variable names.

## 🧪 Verification
- Added a new security test suite (`tests/test_security.py`).
- 26 unit tests passing.
- Verified on real-world large plugins.

## 📦 How to update
```bash
uv sync
```

---
*Helping you build safer and faster QGIS plugins.*
