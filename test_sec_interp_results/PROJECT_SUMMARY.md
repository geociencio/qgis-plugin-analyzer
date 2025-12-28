# 📋 Informe de Análisis de Proyecto: sec_interp
*Generado el: 2025-12-28 11:11:47*

## 📊 Indicadores de Calidad
- **Puntuación de Código**: `37.2/100`
- **Cumplimiento QGIS**: `0/100`

## 🛠️ Hallazgos de Estándares QGIS
Se detectaron **44** desviaciones técnicas.
- 🟡 `.ai-context/context_manager.py:154`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/context_manager.py:161`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/context_manager.py:184`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `core/validation/layer_validator.py:38`: mapLayersByName() puede ser impreciso. Considerar mapLayers() o IDs únicos.
- 🟡 `generate_ai_templates.py:297`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `scripts/clean_imports.py:1`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `scripts/clean_imports.py:62`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `scripts/inspect_qgs_api.py:1`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `logger_config.py:64`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `logger_config.py:132`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `tools/qgis_plugin_analyzer/src/analyzer/cli.py:1`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `tools/qgis_plugin_analyzer/src/analyzer/engine.py:1`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `tools/qgis_plugin_analyzer/src/analyzer/engine.py:73`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `tools/qgis_plugin_analyzer/src/analyzer/utils.py:1`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `sec_interp_plugin.py:264`: mapLayersByName() puede ser impreciso. Considerar mapLayers() o IDs únicos.
- 🔴 `tools/qgis_plugin_analyzer/src/analyzer/scanner.py:12`: Uso de writeAsVectorFormat() obsoleto. Usar writeAsVectorFormatV3().
- 🟡 `tools/qgis_plugin_analyzer/src/analyzer/scanner.py:18`: mapLayersByName() puede ser impreciso. Considerar mapLayers() o IDs únicos.
- 🟡 `tools/qgis_plugin_analyzer/src/analyzer/scanner.py:42`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `scripts/verify_refactor_mock.py:135`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `scripts/verify_refactor_mock.py:179`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `scripts/verify_refactor_mock.py:196`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `scripts/verify_refactor_mock.py:281`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/ai_workflow.py:83`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/ai_workflow.py:693`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/ai_workflow.py:852`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/ai_workflow.py:870`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/ai_workflow.py:889`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/ai_workflow.py:919`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/ai_workflow.py:962`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/ai_workflow.py:978`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `.ai-context/ai_workflow.py:996`: Uso de print() detectado. Usar QgsMessageLog.
- 🔴 `analyze_project_optfixed.py:1591`: Uso de writeAsVectorFormat() obsoleto. Usar writeAsVectorFormatV3().
- 🟡 `analyze_project_optfixed.py:1603`: mapLayersByName() puede ser impreciso. Considerar mapLayers() o IDs únicos.
- 🟡 `analyze_project_optfixed.py:288`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `analyze_project_optfixed.py:1208`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `analyze_project_optfixed.py:1631`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `analyze_project_optfixed.py:2281`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `analyze_project_optfixed.py:2359`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `analyze_project_optfixed.py:2421`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `analyze_project_optfixed.py:2476`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `analyze_project_optfixed.py:2492`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `analyze_project_optfixed.py:2820`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `analyze_project_optfixed.py:2851`: Uso de print() detectado. Usar QgsMessageLog.
- 🟡 `analyze_project_optfixed.py:2863`: Uso de print() detectado. Usar QgsMessageLog.

## 📦 Estándares de Repositorio Oficial
- **Estructura de Archivos**: ✅ OK
- **Metadatos (metadata.txt)**: ✅ OK

## 📈 Métricas Generales
- **Total Files**: 122
- **Total Lines**: 20267