# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
