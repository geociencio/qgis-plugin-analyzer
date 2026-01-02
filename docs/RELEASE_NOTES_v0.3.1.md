# Release Notes v0.3.1: Stability and Diagnostics 🛠️

We are excited to introduce **QGIS Plugin Analyzer v0.3.1**. This maintenance release focuses on system stability, resource management, and professional diagnostic tools, ensuring the analyzer remains robust even when processing massive QGIS projects.

## 🌟 Key Improvements

### 🔧 1. Resource Optimization & Safety
To prevent system crashes and memory exhaustion on large projects, we've implemented several protective measures:
- **Controlled Parallelism**: Worker processes are now limited to a maximum of 4 by default, preventing CPU and RAM spikes on high-core machines.
- **File Size Safety**: Generically large files (over 500KB) are automatically skipped with a warning, protecting the engine from massive generated datasets or logs.
- **Smart ETA**: The progress tracker now uses a moving average for more accurate time estimates without storing all processing history.

### 📝 2. Professional Logging System
No more silent failures! We've replaced simple `print` statements with a robust logging architecture:
- **Persistent Logs**: All analysis details are saved to `analysis_results/analyzer.log`.
- **Deep Diagnostics**: Critical errors now capture and log the full Python traceback, making it easy to identify the root cause of any engine failure.
- **Clean Interface**: Console output remains focused on what matters, while the nitty-gritty details go safely to the log file.

### ⚡ 3. Performance Tuning
- **Matcher Caching**: The `IgnoreMatcher` now caches results for `.analyzerignore` patterns, significantly speeding up the initial file discovery phase on deep directory structures.

## 🐛 Bug Fixes
- **CLI Stability**: Fixed a missing `pathlib` import that caused crashes in certain environments.
- **Rule Consistency**: Standardized rule IDs (`UNPRECISE_LAYER_LOOKUP`, `MANUAL_RESOURCE_PATH`) for better clarity and consistency with the automated test suite.
- **Test Alignment**: Updated all internal tests to match the new optimized engine logic.

## 🚀 Upgrade Now

Upgrade using `uv`:
```bash
uv tool upgrade qgis-plugin-analyzer
```
Or install fresh:
```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-analyzer.git
```

---
*Building a more stable future for PyQGIS development.*
