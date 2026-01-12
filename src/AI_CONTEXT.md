# CONTEXTO PARA IA - src
Generado automáticamente por ProjectAnalyzer v2.0 (Optimizado)

## 📁 ESTRUCTURA DEL PROYECTO

./
    .analyzer_state.json
    AI_CONTEXT.md
    PROJECT_SUMMARY.md
    __init__.py
    analysis_errors.json
    project_context.json
    analyzer/
        __init__.py
        cli.py
        engine.py
        fixer.py
        scanner.py
        semantic.py
        transformers.py
        validators.py
        rules/
            __init__.py
            modernization_rules.py
            qgis_rules.py
        utils/
            __init__.py
            ast_utils.py
            config_utils.py
            logging_utils.py
            path_utils.py
            performance_utils.py
        reporters/
            __init__.py
            html_reporter.py
            markdown_reporter.py
            summary_reporter.py
        models/
            __init__.py
            analysis_models.py
    qgis_plugin_analyzer.egg-info/
        PKG-INFO
        SOURCES.txt
        dependency_links.txt
        entry_points.txt
        top_level.txt


## 🎯 PUNTOS DE ENTRADA
- `analyzer/cli.py`


## 🏗️ PATRONES DETECTADOS

No se detectaron patrones de diseño claros.
## 📈 COMPLEJIDAD Y MÉTRICAS
- **Módulos totales**: 24
- **Líneas de código**: 4,397
- **Funciones**: 134
- **Clases**: 19
- **Complejidad promedio**: 26.6
- **Módulos más complejos**: analyzer/scanner.py, analyzer/engine.py, analyzer/validators.py

## 🔗 DEPENDENCIAS PRINCIPALES

### Third Party (más frecuentes):
- `utils` (14 imports)
- `ast_utils` (6 imports)
- `transformers` (5 imports)
- `validators` (5 imports)
- `path_utils` (4 imports)
- `reporters` (4 imports)
- `performance_utils` (3 imports)
- `rules` (3 imports)
- `urllib` (3 imports)
- `abc` (2 imports)
- `analysis_models` (2 imports)
- `concurrent` (2 imports)
- `config_utils` (2 imports)
- `dataclasses` (2 imports)
- `logging_utils` (2 imports)

## 💡 RECOMENDACIONES DE OPTIMIZACIÓN

### analyzer/reporters/summary_reporter.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (40) con 6 funciones

### analyzer/rules/qgis_rules.py (Prioridad: MEDIA)
- **funciones_demasiado_largas**: Funciones muy largas (promedio 75.0 líneas/función)

### analyzer/reporters/markdown_reporter.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (25) con 6 funciones

### analyzer/transformers.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (29) con 10 funciones

### analyzer/engine.py (Prioridad: ALTA)
- **imports_excesivos**: Muchos imports (30)
- **refactorizacion_complejidad**: Alta complejidad (62) con 10 funciones

## 🕸️  ESTRUCTURA DE DEPENDENCIAS
- **Nodos**: 24
- **Aristas**: 0
- **Densidad**: 0.000
- **Grafo acíclico**: Sí
- **Componentes conectados**: 24

## 🕸️ DIAGRAMA DE DEPENDENCIAS (Conceptuall)
```mermaid
graph TD
```

## 🔑 PALABRAS CLAVE DEL PROYECTO
- **Tecnologías**: .pyc, .py, .txt, .json, .md
- **Patrones**: 
