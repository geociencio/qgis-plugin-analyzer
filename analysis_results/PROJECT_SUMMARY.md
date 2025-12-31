# 📋 Project Analysis Report: qgis_plugin_analyzer
*Generated on: 2025-12-30 21:14:11*

## 📊 Quality Indicators
- **Code Score**: `55.9/100`
- **QGIS Compliance**: `56/100`

## 🛠️ QGIS Standard Findings
Detected **7** technical deviations.
- 🟡 `tests/test_analyzer.py:10`: print() usage detected. Use QgsMessageLog.
- 🟡 `tests/test_scanner.py:62`: mapLayersByName() can be imprecise. Consider mapLayers() or unique IDs.
- 🟡 `tests/test_scanner.py:63`: Manual resource path detected. Use :/plugins/...
- 🟡 `tests/test_scanner.py:19`: print() usage detected. Use QgsMessageLog.
- 🟡 `src/analyzer/utils.py:177`: print() usage detected. Use QgsMessageLog.
- 🟡 `src/analyzer/scanner.py:33`: mapLayersByName() can be imprecise. Consider mapLayers() or unique IDs.
- 🟡 `src/analyzer/scanner.py:51`: print() usage detected. Use QgsMessageLog.

## 📦 Official Repository Standards
- **File Structure**: ❌ Incomplete
  - Missing: `metadata.txt, __init__.py, LICENSE`
  - Missing `classFactory` in `__init__.py`
- **Metadata (metadata.txt)**: 🛠️ Needs Attention
  - Missing fields: `name, description, version, qgisMinimumVersion, author, email`

## 📈 General Metrics
- **Total Files**: 11
- **Total Lines**: 1474