# Plan de Implementación: División de Módulos > 400 líneas

> **Estado**: implementado (2026-10-11)
> **Meta**: llevar `engine.py`, `fixer.py`, `summary_reporter.py` y `commands.py`
> a **≤ 400 líneas** cada uno (límite `module_size_limit` de `forge.toml`),
> sin cambios de comportamiento ni de la superficie de importación pública.
> Origen: `.agent-state/task.md` → *Deferred Follow-ups* (id 4.1).

## Invariantes (no negociables)

- **Import paths estables**: deben seguir funcionando
  `analyzer.engine.{ProjectAnalyzer,ScoringEngine}`,
  `analyzer.fixer.{AutoFixer,check_git_status,create_ast_handler,registry,show_diff}` y
  `analyzer.reporters.summary_reporter.{report_summary,_group_findings_by_severity}`.
- **Patch targets de tests**: preservar `analyzer.fixer.subprocess.run`,
  `analyzer.fixer.check_git_status` y el estático `ProjectAnalyzer._resolve_max_workers`.
- **Registro por side-effect**: el import de los handlers debe seguir siendo *eager*
  (AGENT_LESSONS 2026-10-10) + test de "registro no vacío".
- **Calidad**: `ruff check` + `ruff format` + `mypy` + `pytest` (194) en verde;
  self-analysis `--max-cc 15` en verde.
- **Sin cambios de lógica**: solo reubicación de símbolos + delegación.

---

## Fase 1 — `fixer.py` (466 → ~330). Riesgo: bajo

- Nuevo `src/analyzer/fix_types.py` (~25): `FixContext`, `FixHandlerResult`.
- Nuevo `src/analyzer/fix_handlers.py` (~130): `FixRegistry`, `registry` global,
  `create_ast_handler` y las 4 llamadas `registry.register(...)` (side-effects).
- `src/analyzer/fixer.py`: conserva `check_git_status`, `show_diff`, `AutoFixer`;
  **re-exporta** los símbolos movidos para no romper imports ni patch targets.
- Nuevo `tests/test_fixer_registry.py`: verifica que el registro queda poblado al importar.

## Fase 2 — `summary_reporter.py` (424 → ~330). Riesgo: bajo

- Nuevo `src/analyzer/reporters/console.py` (~50): `print_header`, `print_separator`,
  `print_success`, `print_colored_score` (módulo hoja, sin ciclos).
- Nuevo `src/analyzer/reporters/security_summary.py` (~95): `_group_findings_by_severity`,
  `_print_security_finding`, `_print_security_findings_by_severity`, `_report_security`.
- `summary_reporter.py`: `report_summary`, `_report_total`, `_report_by_*`, helpers de
  issues; re-exporta los símbolos movidos para back-compat.

## Fase 3 — `engine.py` (561 → ~392). Riesgo: medio

`ProjectAnalyzer` **permanece** en `engine.py` (no se convierte en paquete); sus métodos
delegan en funciones libres extraídas:

- Nuevo `src/analyzer/ruff_audit.py` (~85): `run_ruff_audit(project_path, *, strict)` (−57).
- `src/analyzer/semantic.py`: añadir `run_semantic_analysis(...)` (−37).
- Nuevo `src/analyzer/qgis_checks.py`: `run_qgis_checks(...)` (−32).
- Nuevo `src/analyzer/scope_filter.py`: `filter_issues_by_scope(modules_data, scope)` (−33).
- `src/analyzer/utils/performance_utils.py`: añadir `resolve_max_workers(workers)` (−10);
  el estático `_resolve_max_workers` mantiene su firma y delega.

## Fase 4 — `commands.py` (408 → 309). Riesgo: bajo

- Extraída la detección de caché obsoleta a `src/analyzer/utils/stale_cache.py`
  (`detect_stale_cache` + helpers privados `_parse_analyzed_at`,
  `_find_newer_source_files`, `_humanize_age`); `handle_summary` la consume.
- `tests/test_cache_handling.py` actualizado al nuevo módulo.
- `commands.py` conserva los nombres que los tests parchean
  (`analyzer.commands.ProjectAnalyzer`, `analyzer.commands.report_summary`).

---

## Resultado (2026-10-11)

| Módulo | Antes | Después |
| :--- | ---: | ---: |
| `engine.py` | 561 | 398 |
| `fixer.py` | 466 | 335 |
| `reporters/summary_reporter.py` | 424 | 294 |
| `commands.py` | 408 | 309 |

Nuevos módulos: `ruff_audit.py`, `qgis_checks.py`, `scope_filter.py`,
`parallel_analysis.py`, `fix_types.py`, `fix_handlers.py`,
`reporters/console.py`, `reporters/security_summary.py`, `utils/stale_cache.py`.

Verificación: `ruff check`/`format` + `mypy` limpios; **195 tests**; self-analysis
`--max-cc 15` OK (máx CC 13); stability 53.9→54.9, maintainability 86.7→87.3.

---

## Validación tras cada fase

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy src/
uv run python -m pytest tests/ -q
uv run qgis-analyzer analyze . --max-cc 15
```

**Orden**: Fase 1 → 2 → 3 → 4. Cierre con `/create-commit` (mensaje `refactor(...)`).
