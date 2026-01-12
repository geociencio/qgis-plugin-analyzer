# RESUMEN DEL PROYECTO - qgis_plugin_analyzer
Fecha de análisis: 2026-01-11 21:13:15
Versión del analizador: 2.0 (Optimizado)

## 📊 MÉTRICAS CLAVE
- **Total módulos**: 38
- **Líneas de código**: 10,059
- **Tamaño total**: 1.7 MB
- **Complejidad promedio**: 42.8
- **Cobertura de docstrings**: 50.0%
- **Score de calidad**: 50.2/100
- **Archivos de test**: 42

## 📁 ESTRUCTURA
- **Archivos Python**: 45
- **Total archivos**: 183
- **Tipo de archivos principales**: .pyi, .json, .py, .so, .md

## 🚨 PROBLEMAS CRÍTICOS

### 🔒 Problemas de Seguridad:
- **migration/ai-context-core/src/ai_context_core/analyzer/issues.py**: 15 problemas críticos
- **.ai-context/analyze_project_optfixed.py**: 15 problemas críticos

### 🏗️ Deuda Técnica Crítica:
- **.ai-context/analyze_project_optfixed.py**: 4 issues (score: 8)
- **.ai-context/ai_workflow.py**: 3 issues (score: 7)
- **src/analyzer/engine.py**: 4 issues (score: 7)
- **src/analyzer/scanner.py**: 3 issues (score: 6)
- **migration/ai-context-core/src/ai_context_core/analyzer/dependencies.py**: 3 issues (score: 5)

## 📦 ESTÁNDARES DE PLUGIN QGIS
- **Score de Cumplimiento**: 50.0/100
- ❌ **Archivos faltantes**: metadata.txt, __init__.py

## 💡 RECOMENDACIONES PRINCIPALES

### migration/ai-context-core/src/ai_context_core/analyzer/fs_utils.py
- Alta complejidad (61) con 13 funciones

### migration/ai-context-core/src/ai_context_core/analyzer/ast_utils.py
- Alta complejidad (61) con 9 funciones

### src/analyzer/scanner.py
- Alta complejidad (171) con 18 funciones
- Módulo muy grande (795 líneas)

## 📈 DISTRIBUCIÓN DE COMPLEJIDAD
- low (0-5): 11 módulos (28.9%)
- medium (6-15): 2 módulos (5.3%)
- high (16-30): 8 módulos (21.1%)
- very_high (31+): 17 módulos (44.7%)
