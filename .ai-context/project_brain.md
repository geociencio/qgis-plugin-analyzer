# Cerebro del Proyecto: qgis-plugin-analyzer

## 🚨 Reglas Críticas (Globales)
- **ESCAPADO DE METADATOS**: El analizador debe detectar y sugerir escapar % como %% en metadata.txt de plugins QGIS.
- **INDEPENDENCIA DE RUNTIME**: Este proyecto NO debe depender de PyQGIS o Qt en runtime, solo analiza código estáticamente.

## Visión General
Motor de análisis estático y auto-fix para plugins de QGIS (PyQGIS). Combina reglas AST personalizadas con Ruff para detectar problemas de calidad, cumplimiento con estándares QGIS, y generar contexto optimizado para IAs.

<!-- METRICS_START -->
## 📊 Métricas de Salud (Actualizado: 2026-01-11)
- **Score de Calidad**: 50.2/100
- **Score Cumplimiento QGIS**: 50.0/100
- **Líneas de Código**: 10,059 en 38 módulos.
- **Complejidad Promedio**: 42.8. (Módulos más complejos: `.ai-context/analyze_project_optfixed.py`, `src/analyzer/scanner.py`, `.ai-context/ai_workflow.py`).
<!-- METRICS_END -->

## 🏗️ Arquitectura Principal (Patrones Detectados)
- **Motor de Reglas AST**: Procesamiento paralelo de archivos Python con análisis semántico profundo.
- **Auto-Fix Interactivo**: Transformaciones AST seguras con verificación de Git y previsualizaciones.
- **Pipeline de Análisis**: Escaneo → Análisis Semántico → Generación de Reportes (JSON/Markdown/HTML).
- **Zero Runtime Dependencies**: Solo usa la librería estándar de Python (Ruff como herramienta externa).

## 🔗 Componentes Críticos
1. **Engine (`analyzer/engine.py`)**: Orquestador principal del análisis paralelo (Complejidad: 62).
2. **Scanner (`analyzer/scanner.py`)**: Motor de reglas AST para validación de QGIS.
3. **Fixer (`analyzer/fixer.py`)**: Sistema de auto-corrección con transformaciones AST.
4. **Semantic Analyzer (`analyzer/semantic.py`)**: Análisis de dependencias y detección de ciclos.
5. **Reporters (`analyzer/reporters/`)**: Generación de reportes en múltiples formatos.

## 🚨 Deuda Técnica y Prioridades
- **Alta Complejidad**: `analyzer/engine.py` (62) requiere refactorización en sub-módulos.
- **Cobertura de Docstrings**: Mejorar del 62.5% actual al 80%+.
- **Testing**: Actualmente 0 archivos de test detectados, necesita suite completa.
- **Falsos Positivos**: El analizador se evalúa a sí mismo como plugin QGIS, necesita modo "self-analysis".
