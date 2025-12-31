# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-12-30

### Added
- **Deep Semantic Analysis** (Roadmap Point 1)
  - Dependency graph with circular import detection
  - Resource validation (Qt `.qrc` files)
  - Signal/Slot safety checks for missing slot methods
  - Module coupling metrics (fan-in/fan-out)
- **Interactive Auto-Fix Mode** (Roadmap Point 2)
  - `fix` command with dry-run mode by default
  - AST-based transformers for code corrections:
    - `GDALImportFixer`: `import gdal` → `from osgeo import gdal`
    - `LegacyImportFixer`: `PyQt4/PyQt5` → `qgis.PyQt`
    - `PrintToLogFixer`: `print()` → `QgsMessageLog.logMessage()`
    - `I18nFixer`: Wrap hardcoded strings in `self.tr()`
  - Safety features: git status check, interactive diff preview, confirmation prompts
  - Rule filtering with `--rules` flag
- **Repository Compliance Suite** (Roadmap Point 3)
  - Binary scanner: Detect prohibited `.exe`, `.dll`, `.so` files
  - Package size calculator with 20MB limit warning
  - URL validator for `metadata.txt` links (homepage, tracker, repository)
  - Integration into scoring system with penalties
- **Enhanced Configuration Profiles** (Roadmap Point 4)
  - Rule-level configuration in `pyproject.toml`
  - Custom severity levels: `error`, `warning`, `info`, `ignore`
  - Nested TOML section support: `[tool.qgis-analyzer.profiles.NAME.rules]`
  - Backward compatible (works without rules config)

### Changed
- Updated `load_profile_config()` to parse `rules` section
- Enhanced minimal TOML parser for nested sections
- `QGISASTVisitor` now accepts `rules_config` parameter
- Scoring system penalizes binaries (-50 pts) and size violations (-10 pts)

### Documentation
- Created `COMPETITIVE_ANALYSIS.md` comparing with flake8-qgis and pylint-plugin-utils
- Updated walkthrough artifacts for each feature

## [0.4.0] - 2025-12-29
### Changed
- **Zero Runtime Dependencies**: Removed all external runtime dependencies (`tomli`, `dominate`). The analyzer now uses a built-in minimal TOML generator and manual HTML reporting.
- **Migration to Unittest**: Refactored the entire test suite from `pytest` to the native `unittest` framework, removing `pytest` from the development stack.
- **Optimized Deployment**: Reduced project footprint by eliminating non-essential packages.

### Removed
- **Project Generator (`init`)**: Project generation capabilities were removed from the analyzer to focus strictly on static analysis. The code has been exported to `generator_export`.

## [0.3.1] - 2025-12-29
### Added
- **Professional Logging System**: Persistent logging to `analysis_results/analyzer.log` with detailed tracebacks for troubleshooting.
- **Resource Management**: Optimized concurrency (limited to 4 workers) and file size safety (skips files >500KB) to prevent system crashes on large projects.
- **Cache Optimization**: Added results cache to `IgnoreMatcher` for faster file scanning.

### Fixed
- **CLI Stability**: Resolved `NameError: pathlib` and improved top-level exception handling.
- **Audit Rule IDs**: Renamed `UNPRECISE_LAYER` to `UNPRECISE_LAYER_LOOKUP` and `MANUAL_PATH` to `MANUAL_RESOURCE_PATH` for clarity and test consistency.

## [0.3.0] - 2025-12-29
### Added
- **Ruff Integration**: Native execution of Ruff for Python standard linting.
- **AST Audit Engine**: Migration of critical rules to Abstract Syntax Tree (AST) for higher precision.
- **New QGIS Rules**: 
  - `QGIS_PROTECTED_MEMBER`: Detection of unstable protected imports (`qgis._core`, etc.).
  - `IFACE_AS_ARGUMENT`: Detection of `QgisInterface` passed as argument (standards QGS105).
  - `GDAL_DIRECT_IMPORT`: Warning for direct `gdal` imports instead of `osgeo.gdal`.
  - `MANDATORY_CLEANUP`: Validation of `unload()` presence when `initGui()` is used.
- **Advanced Profiles**: Configurable profiles (`default`, `release`) in `pyproject.toml` with strict modes.
- **HTML Reports**: Professional and visual report generation using `dominate`.
- **Boilerplate System (`init`)**: Project generation for Processing, GUI, and Map Tool plugins.
- **Template Safety**: Use of `.tmpl` extension for boilerplate files to avoid IDE syntax errors.

### Fixed
- **Stability**: Resolved `KeyError: complexity` crashes during syntax errors.
- **Reliability**: Restored missing system imports in utility modules.

## [0.2.0] - 2025-12-28
### Added
- Support for `.analyzerignore` files to exclude specific files and directories from analysis.
- Robust pattern matching using the native `fnmatch` module (no external dependencies).


### Added
- Initial project structure for QGIS Plugin Analyzer.
- Professional static analysis engine using Python AST and Regex.
- Compliance rules for QGIS standards (i18n, obsolete APIs, threading, etc.).
- Official repository standards validation (`metadata.txt`, `__init__.py`, `LICENSE`).
- Multi-process support for high-performance analysis.
- Markdown and JSON reporting system.
- Unit test suite for scanner and validation logic using `pytest`.
- Development dependency management with `uv`.

### Fixed
- Corrected scoring reporting bug where `qgis_score` appeared as 0 in `PROJECT_SUMMARY.md`.
- Refined `MANUAL_RESOURCE_PATH` regex for better detection of manual icon/UI paths.
- Fixed regex typo and lookahead logic in `scanner.py`.

## [0.0.1] - 2025-12-25
- Conceptual prototype, research, and comparative analysis.
