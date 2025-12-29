# 📋 Project Analysis Report: qgis_plugin_analyzer
*Generated on: 2025-12-29 01:07:49*

## 📊 Quality Indicators
- **Code Score**: `57.0/100`
- **QGIS Compliance**: `44/100`

## 🛠️ QGIS Standard Findings
Detected **13** technical deviations.
- 🟡 `src/analyzer/cli.py:61`: print() usage detected. Use QgsMessageLog.
- 🟡 `tests/test_scanner.py:53`: mapLayersByName() can be imprecise. Consider mapLayers() or unique IDs.
- 🟡 `tests/test_scanner.py:54`: Manual resource path detected. Use :/plugins/...
- 🟡 `tests/test_scanner.py:6`: print() usage detected. Use QgsMessageLog.
- 🟡 `src/analyzer/generator.py:1`: print() usage detected. Use QgsMessageLog.
- 🟡 `src/analyzer/generator.py:25`: print() usage detected. Use QgsMessageLog.
- 🟡 `src/analyzer/engine.py:68`: print() usage detected. Use QgsMessageLog.
- 🟡 `src/analyzer/engine.py:142`: print() usage detected. Use QgsMessageLog.
- 🟡 `src/analyzer/engine.py:151`: print() usage detected. Use QgsMessageLog.
- 🟡 `src/analyzer/utils.py:20`: print() usage detected. Use QgsMessageLog.
- 🟡 `src/analyzer/utils.py:157`: print() usage detected. Use QgsMessageLog.
- 🟡 `src/analyzer/scanner.py:33`: mapLayersByName() can be imprecise. Consider mapLayers() or unique IDs.
- 🟡 `src/analyzer/scanner.py:51`: print() usage detected. Use QgsMessageLog.

## 📦 Official Repository Standards
- **File Structure**: ❌ Incomplete
  - Missing: `metadata.txt, __init__.py, LICENSE`
  - Missing `classFactory` in `__init__.py`
- **Metadata (metadata.txt)**: 🛠️ Needs Attention
  - Missing fields: `name, description, version, qgisMinimumVersion, author, email`

## 📈 General Metrics
- **Total Files**: 14
- **Total Lines**: 1392