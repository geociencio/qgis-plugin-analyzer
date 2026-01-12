# CONTEXTO PARA IA - qgis_plugin_analyzer
Generado automáticamente por ProjectAnalyzer v2.0 (Optimizado)

## 📁 ESTRUCTURA DEL PROYECTO

./
    .analyzerignore
    .gitignore
    .pre-commit-hooks.yaml
    CHANGELOG.md
    CONTRIBUTING.md
    LICENSE
    README.md
    ... (+6 más)
    src/
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
    


## 🎯 PUNTOS DE ENTRADA
- `.ai-context/ai_workflow.py`
- `.ai-context/analyze_project_optfixed.py`
- `.ai-context/context_manager.py`
- `.venv/lib/python3.13/site-packages/mypy/__main__.py`
- `.venv/lib/python3.13/site-packages/mypy/dmypy/__main__.py`
- `.venv/lib/python3.13/site-packages/mypy/main.py`
- `.venv/lib/python3.13/site-packages/mypy/stubgen.py`
- `.venv/lib/python3.13/site-packages/mypy/stubgenc.py`
- `.venv/lib/python3.13/site-packages/mypyc/__main__.py`
- `.venv/lib/python3.13/site-packages/mypyc/irbuild/main.py`

... y 3 más

## 🏗️ PATRONES DETECTADOS
- **MVC**: Detectado (confianza: 100%)
- **REPOSITORY**: Detectado (confianza: 100%)
- **FACTORY**: Detectado (confianza: 80%)
## 📈 COMPLEJIDAD Y MÉTRICAS
- **Módulos totales**: 38
- **Líneas de código**: 10,059
- **Funciones**: 305
- **Clases**: 32
- **Complejidad promedio**: 42.8
- **Módulos más complejos**: .ai-context/analyze_project_optfixed.py, src/analyzer/scanner.py, .ai-context/ai_workflow.py

## 🔗 DEPENDENCIAS PRINCIPALES

### Third Party (más frecuentes):
- `utils` (14 imports)
- `ast_utils` (7 imports)
- `transformers` (5 imports)
- `validators` (5 imports)
- `concurrent` (4 imports)
- `path_utils` (4 imports)
- `reporters` (4 imports)
- `performance_utils` (3 imports)
- `rules` (3 imports)
- `urllib` (3 imports)
- `abc` (2 imports)
- `analysis_models` (2 imports)
- `config` (2 imports)
- `config_utils` (2 imports)
- `dataclasses` (2 imports)

## 💡 RECOMENDACIONES DE OPTIMIZACIÓN

### migration/ai-context-core/src/ai_context_core/analyzer/fs_utils.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (61) con 13 funciones

### migration/ai-context-core/src/ai_context_core/analyzer/ast_utils.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (61) con 9 funciones

### src/analyzer/scanner.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (171) con 18 funciones
- **modulo_demasiado_grande**: Módulo muy grande (795 líneas)

### src/analyzer/transformers.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (29) con 10 funciones

### src/analyzer/semantic.py (Prioridad: ALTA)
- **refactorizacion_complejidad**: Alta complejidad (42) con 10 funciones

## 🕸️  ESTRUCTURA DE DEPENDENCIAS
- **Nodos**: 38
- **Aristas**: 0
- **Densidad**: 0.000
- **Grafo acíclico**: Sí
- **Componentes conectados**: 38

## 🕸️ DIAGRAMA DE DEPENDENCIAS (Conceptuall)
```mermaid
graph TD
```

## 🔑 PALABRAS CLAVE DEL PROYECTO
- **Tecnologías**: .pyi, .json, .py, .so, .md, .pyc, .c, .yaml
- **Patrones**: mvc, repository, factory
