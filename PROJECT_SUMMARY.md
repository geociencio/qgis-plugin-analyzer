# PROJECT SUMMARY - qgis_plugin_analyzer
Analysis Date: 2026-04-26 21:37:21
Analyzer Version: 3.1.1 (Ai-Context-Core)

## 📊 KEY METRICS
- **Quality Score**: 49.8/100
- **Source Lines (SLOC)**: 4,164
- **Total Physical Lines**: 7,390
- **Maintainability**: 44.9
- **Test Coverage**: 0 test files

## 📁 STRUCTURE
**Total Modules**: 53

```tree
./
    .ai_context_cache.json
    .analyzer_state.json
    .analyzerignore
    .coverage
    .gitignore
    .pre-commit-hooks.yaml
    AI_CONTEXT.md
    ... (+17 more)
    src/
        .analyzer_state.json
        AI_CONTEXT.md
        PROJECT_SUMMARY.md
        __init__.py
        analysis_errors.json
        project_context.json
        analyzer/
            __init__.py
            aggregators.py
            commands.py
            engine.py
            fixer.py
            main.py
            scanner.py
            ... (+6 more)
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
            visitors/
                __init__.py
                base.py
                composite_visitor.py
                i18n_visitor.py
                imports_visitor.py
                metrics_visitor.py
                qgis_rules_visitor.py
                ... (+2 more)
            cli/
                __init__.py
                app.py
                base.py
                commands/
                    __init__.py
                    analyze.py
                    fix.py
                    graph.py
                    init.py
                    list_rules.py
                    security.py
                    ... (+2 more)
        qgis_plugin_analyzer.egg-info/
            PKG-INFO
            SOURCES.txt
            dependency_links.txt
            entry_points.txt
            top_level.txt
    test_sec_interp_results/
        PROJECT_SUMMARY.md
        project_context.json
    tests/
        test_advanced_features.py
        test_analyzer.py
        test_ast_utils_extended.py
        test_cli.py
        test_fixer.py
        test_high_complexity.py
        test_i18n_heuristics.py
        ... (+11 more)
    english_test_results/
        PROJECT_SUMMARY.md
        project_context.json
    docs/
        DEVELOPMENT_LOG.md
        user_guide/
            COMMANDS_GUIDE.md
            TESTING_IN_QGIS.md
        releases/
            notes/
                RELEASE_NOTES_v0.2.0.md
                RELEASE_NOTES_v0.3.0.md
                RELEASE_NOTES_v0.3.1.md
                RELEASE_NOTES_v0.4.0.md
                RELEASE_NOTES_v0.5.0.md
                RELEASE_NOTES_v0.5.1.md
                RELEASE_NOTES_v0.6.0.md
                ... (+15 more)
            github/
                GITHUB_RELEASE_v0.6.1.md
                GITHUB_RELEASE_v0.6.2.md
                GITHUB_RELEASE_v0.7.0.md
                GITHUB_RELEASE_v0.9.0.md
                GITHUB_RELEASE_v1.0.0.md
                GITHUB_RELEASE_v1.1.0.md
                GITHUB_RELEASE_v1.2.0.md
                GITHUB_RELEASE_v1.4.0.md
        research/
            CLI_COMMANDS_ROADMAP.md
            COMPETITIVE_ANALYSIS.md
            FUTURE_ROADMAP.md
            PYPI_STANDARDS_RESEARCH.md
            PYTHON_QUALITY_RESEARCH.md
            QWEN.md
            ROADMAP_IMPROVEMENTS.md
            ... (+3 more)
        development/
            COMMIT_GUIDELINES.md
            DEVELOPMENT_LOG.md
            REMAINING_ISSUES.md
            ROADMAP.md
            SCORING_STANDARDS.md
            SUGERENCIAS_AI_CONTEXT.md
            SUGGESTED_IMPROVEMENTS.md
            uv_modernization_guide.md
        reports/
            ANALYSIS_REPORT.md
        dev_sessions/
            2026-02-02_refactor_architecture.md
            2026-02-03_repository_validation.md
            2026-04-05_v1.11.0_release.md
            session_2026-02-14_task.md
            session_2026-02-14_walkthrough.md
        maintenance/
            session_2026-04-05_agent_gen5_sync.md
            session_2026-04-26_bug_audit.md
            session_2026-04-26_quality_blindage.md
            session_2026-04-26_v1.12.0_release.md
    debug_summary/
    scripts/
        mcp_server.py
        run_tests_in_qgis.py
        security_scan.py
        skill_sync.py
    migration/
    self_analysis_results/
        PROJECT_SUMMARY.md
        analyzer.log
        project_context.json
    self_analysis_results_v2/
        PROJECT_SUMMARY.md
        analyzer.log
        project_context.json
    analysis_results/
        PROJECT_SUMMARY.html
        PROJECT_SUMMARY.md
        analyzer.log
        project_context.json
    analysis_results_release/
        PROJECT_SUMMARY.md
        analyzer.log
        project_context.json
    scaffold/
        qgis/
            skills/
                qa-docker/
                    SKILL.md
                qgis-core/
                    SKILL.md
                qgis-migration-4x/
                    SKILL.md
                ui-framework/
                    SKILL.md
            workflows/
                audit-plugin.md
                release-plugin.md
                run-tests-in-qgis.md
        mining/
            skills/
                geological-logic/
                    SKILL.md
    dist/
        qgis_plugin_analyzer-1.13.0-py3-none-any.whl
        qgis_plugin_analyzer-1.13.0.tar.gz
```

## 🚨 CRITICAL ISSUES
### 🔒 Security Issues:
- **src/analyzer/__init__.py**: 1 issues (Max: HIGH)
- **src/analyzer/cli/app.py**: 1 issues (Max: HIGH)
- **src/analyzer/cli/commands/serve.py**: 1 issues (Max: HIGH)

## 💡 MAIN RECOMMENDATIONS
### src/analyzer/commands.py
- Consider breaking down large logic
### src/analyzer/fixer.py
- Consider breaking down large logic
### src/analyzer/reporters/html_reporter.py
- Consider breaking down large logic

## 🏗️ DESIGN PATTERNS
### Decorator
- **register** in `src/analyzer/fixer.py` (50%)
- **create_ast_handler** in `src/analyzer/fixer.py` (50%)
- **register** in `src/analyzer/security_checker.py` (50%)

## 📝 ARCHITECTURE NOTES
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


## 🔄 GIT ANALYSIS
### Code Churn (last 30 days)
- **Files Changed**: 250
- **Additions**: +25178
- **Deletions**: -19873
- **Total Churn**: 45051

### 🔥 Hotspots
- `src/analyzer/engine.py`: 32 commits
- `src/analyzer/scanner.py`: 27 commits
- `src/analyzer/cli.py`: 18 commits
- `src/analyzer/utils.py`: 14 commits
- `src/analyzer/validators.py`: 13 commits

## 📈 COMPLEXITY DISTRIBUTION
- **Average Complexity**: 14.85
- **Max Complexity**: 58
