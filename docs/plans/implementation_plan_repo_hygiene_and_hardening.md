# Plan de Implementación: Higiene del Repo, Robustez y CI (v1.15.0)

> **Estado**: propuesto — revisado por `/ia-critic` (hallazgos corregidos); pendiente
> de aprobación del USER antes de implementar.
> **Meta**: sanear el repositorio (artefactos generados versionados), endurecer la
> robustez del CLI (opt-out por regla, audit de ruff fiable, normalización de paths),
> añadir CI de calidad y cerrar/decidir los huecos funcionales del reparto con el
> proyecto hermano `ai-context-core` (ADR-0008, en
> `../../ai-context-core/docs/adr/0008-context-only-contract.md`; **no** existe
> `docs/adr/` en este repo).
> **Referencia de evidencia**: self-run `uv run qgis-analyzer analyze src/analyzer --json`
> (2026-10-10): 53 archivos, 7,966 líneas, `quality_score 54.5`, `maintainability 88.1`,
> `security 100`, 0 dependencias circulares, `ruff_findings 0`.

## 0. Evidencia medida

- **Funciones que violan el gate `--max-cc 15`** (CC **> 15**; `_enforce_max_cc` usa
  `cc > max_cc`, `src/analyzer/commands.py:161`): `extract_runtime_imports_from_ast`
  (`src/analyzer/utils/ast_utils.py:165`, CC 22), `apply_fixes` (`src/analyzer/fixer.py:302`,
  CC 18), `handle_analyze` (`src/analyzer/commands.py:86`, CC 16). En el límite
  (CC == 15) pero **sin violar** el gate: `visit_For`
  (`src/analyzer/visitors/standards_visitor.py:117`) y `visit_Constant`
  (`src/analyzer/visitors/i18n_visitor.py:268`).
- **Complejidad agregada por módulo** (campo `complexity` a nivel de módulo en el
  JSON, no la suma de CC de sus funciones): `commands.py` 54,
  `visitors/standards_visitor.py` 50, `utils/ast_utils.py` 44, `reporters/summary_reporter.py` 44,
  `fixer.py` 37, `semantic.py` 36, `validators.py` 36.
- **Formato ruff en rojo** (N1): `ruff format --check .` falla hoy en
  `scripts/sync_metrics.py` y `tests/test_i18n_wrappers.py` (trackeados, sin formatear).
- **Artefactos trackeados** (raíz y `src/`) — ver Fase 0.
- **Sin CI de calidad**: solo `.github/workflows/release.yml` (build + publish PyPI).

---

## Fase 0 — Higiene del repositorio (bloqueante, alto ROI)

Artefactos generados/efímeros versionados (git ignora solo lo no trackeado; hay que
`git rm --cached`):

**Raíz**
- `.ai_context_cache.json`, `.analyzer_state.json`, `.coverage`, `analysis.log`,
  `analysis_errors.json`, `bugreport.md`, `reproduce_bug.py`
- `AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json`
- `test_sec_interp_results/{PROJECT_SUMMARY.md,project_context.json}` (ignorado pero trackeado)
- `analysis_results_release/{PROJECT_SUMMARY.md,project_context.json,analyzer.log}`

**Subárbol `src/`**
- `src/.analyzer_state.json`, `src/AI_CONTEXT.md`, `src/PROJECT_SUMMARY.md`,
  `src/analysis_errors.json`, `src/project_context.json`

**Acciones**
1. `git rm --cached` de la lista anterior (conservando copia local si se desea).
2. Ampliar `.gitignore` para cubrir **todos** los artefactos retirados y sus
   variantes `src/`, no solo los no-trackeados: añadir `analysis_results_release/`,
   `debug_summary/`, `migration/`, `.ai_context_cache.json`, `.analyzer_state.json`,
   `.coverage`, `analysis.log`, `analysis_errors.json`, `AI_CONTEXT.md`,
   `PROJECT_SUMMARY.md`, `project_context.json`, `bugreport.md`, `reproduce_bug.py`.
   Varios son ficheros **activos** (`git status` muestra ` M AI_CONTEXT.md`,
   ` M PROJECT_SUMMARY.md`, ` M project_context.json`); sin ignorarlos reaparecerán
   como ruido tras el `git rm --cached`.
3. Borrar el directorio `migration/` (hoy vacío y sin trackear). **Nota**: la
   supuesta causalidad con el error histórico `'str' object has no attribute 'stat'`
   **no está corroborada** en la documentación; el borrado se justifica por ser un
   directorio vacío, no por esa causa.
4. [DECIDIDO 2026-10-10] `bugreport.md`/`reproduce_bug.py` **archivados** en
   `docs/development/` (`git mv`), conservando el caso de estudio. No se ignoran
   (siguen trackeados), por eso quedan **fuera** del criterio de vaciado.

**Criterio de aceptación**: la lista **explícita** de artefactos retirados debe
quedar vacía en `git ls-files` (el regex original solo cubría 4 patrones y dejaba
fuera `.analyzer_state.json`, `.coverage`, `analysis.log`, `AI_CONTEXT.md` y los
equivalentes `src/`). Verificar con:

```bash
git ls-files | grep -E '(^|/)(\.ai_context_cache\.json|\.analyzer_state\.json|\.coverage|analysis\.log|analysis_errors\.json|AI_CONTEXT\.md|PROJECT_SUMMARY\.md|project_context\.json)$|^(src/)?(test_sec_interp_results|analysis_results_release)/'
# → debe quedar vacío
```

(el anclaje `(^|/)` evita falsos positivos como `docs/development/SUGERENCIAS_AI_CONTEXT.md`;
`bugreport.md`/`reproduce_bug.py` se omiten porque se **archivan**, no se eliminan).

---

## Fase 1 — Robustez del CLI

### 1.1 Opt-out `# noqa: <CODE>` transversal
Hoy solo `i18n_visitor.py:309` honra `# no-i18n`/`# noqa`. El resto de reglas
(`MISSING_DOCSTRING`, `MISSING_TYPE_HINTS`, `SPATIAL_INDEX`, …) no tienen supresión.
(Nota: `SIGNAL_LEAK` citado en la versión previa **no** es un rule id real; los
demostrativos válidos son `MISSING_DOCSTRING`/`MISSING_TYPE_HINTS`.)
- Extraer un detector de líneas `# noqa[: CODE]` (tokenize) reutilizable. El módulo
  hermano a imitar es `../../ai-context-core/src/ai_context_core/analyzer/visitors/noqa.py`
  (proyecto externo, ruta relativa a este repo), pero **es específico de F401**;
  para soportar `# noqa: CODE` genérico hace falta un mapa explícito `rule_id → código`.
- Aplicarlo de forma **centralizada** en `CompositeVisitor.visit`
  (`composite_visitor.py:152-155`), que ya agrega `self.issues`, filtrando los
  hallazgos cuya línea cae en un span `# noqa`. Evitar la alternativa "en cada
  regla": `BaseVisitor` (`base.py:13-30`) no expone `lines` y propagarlo a todos los
  visitors añade acoplamiento. Las líneas ya están pre-cargadas en el scanner
  (`scanner.py:150`), por lo que no hay I/O nuevo (respeta "sin I/O en visitors").
- [DECIDIDO 2026-10-10] `# noqa` desnudo **suprime todas** las reglas de esa línea
  (compatible con ruff y con el comportamiento i18n actual); `# noqa: CODE` suprime
  solo las reglas nombradas. Se preserva `# no-i18n` en `i18n_visitor.py:309`.
- Detector reutilizable en `src/analyzer/visitors/noqa.py`
  (`collect_noqa_directives`, basado en `tokenize`, ignora `# noqa` dentro de strings).
- Test dedicado `tests/test_noqa_suppression.py`: `# noqa: MISSING_TYPE_HINTS`
  suprime solo esa regla (no `MISSING_DOCSTRING`); `# noqa` desnudo suprime toda la línea.

### 1.2 Audit de ruff fiable
`engine.py:128` (`run_ruff_audit`) ejecuta `ruff` desde el PATH y, ante fallo,
devuelve `findings=[]` con `exit_code=-1` solo en log (puede confundirse con "limpio").
- Invocar `sys.executable -m ruff` para no depender del PATH. **No** usar
  `config.ruff_path`: ese campo no existe en `ProjectConfig` (`engine.py:64-73`);
  si se quiere configurable, añadirlo explícitamente a `ProjectConfig`.
- Exponer `"tool_unavailable": true` en el JSON cuando no se ejecuta.
- Documentar el select de `--strict` (`engine.py:148-149` reintroduce `D`, `C90`,
  `UP`, …; **no** incluye `ANN`).
- Añadir test de la ruta de fallback (`tool_unavailable`) con ruff ausente.

### 1.3 Normalización de paths (str vs `pathlib`)
Normalizar a `pathlib.Path` en las fronteras (`scanner.py`, `validators.py:276`,
`scanner.py:165/227`) donde se hace `.stat()`. Añadir test de regresión con entradas
`str` y `Path`.

**Criterio de aceptación**: `# noqa: SIGNAL_LEAK` suprime la incidencia; con ruff
ausente el JSON lo declara; pasar `str` a los workers no rompe.

---

## Fase 2 — Rendimiento

### 2.1 Workers configurables
`engine.py:98` fija `self.max_workers = min(os.cpu_count() or 4, 4)` con el
comentario "to prevent OOM".
- [HECHO 2026-10-10] Configurable vía la clave `workers` del profile
  (`[tool.qgis-analyzer.profiles.<p>]`) y CLI `--workers`, con default
  **`min(4, max(1, cpu-1))`** y clamp a `1..4` (preserva el techo anti-OOM).
  `ProjectAnalyzer._resolve_max_workers` centraliza la resolución; el valor de
  CLI tiene precedencia sobre el del profile.
- [HECHO 2026-10-10] Batching mediante `scanner.analyze_chunk_worker` + `_chunk_files`
  (chunks de `len(files) // (workers*4)`), conservando `submit`/`as_completed` y el
  progreso por fichero (evita el rework de `map(chunksize=)` señalado por el auditor).

### 2.2 Caché con invalidación real — DIFERIDO (2026-10-10)
No existe hoy caché de workers: `analyze_module_worker(cached_data=...)` es un
parámetro huérfano sin cablear; la "caché" real es el
`analysis_results/project_context.json` que lee `summary` (staleness por `mtime`
en `commands.py:_detect_stale_cache`). Implementar caché incremental por hash de
contenido + `--no-cache` es una feature aparte (mayor superficie y riesgo de
invalidez); se pospone a un plan propio.

---

## Fase 3 — CI / QA

- [HECHO Fase 3a 2026-10-10] `.github/workflows/ci.yml` (matrix 3.11–3.13):
  `ruff check`, `ruff format --check`, `mypy src/` y `pytest`. N1 resuelto
  (`ruff format .` aplicado). `[tool.pytest.ini_options]` (testpaths, pythonpath)
  añadido para que `uv run pytest` resuelva el layout `src/`.
- [HECHO Fase 3b 2026-10-10] `pytest-cov` añadido al grupo dev; la CI corre
  `pytest --cov=analyzer --cov-report=term-missing --cov-fail-under=70`
  (cobertura real 74%). El self-gate `uv run qgis-analyzer analyze . --max-cc 15`
  está activado (Fase 4 dejó 0 funciones con CC > 15). `forge.toml [project].analyzer_command`
  **no lo lee GitHub Actions**; el workflow fija el comando explícitamente.
- `tests/conftest.py` sigue ausente; con `[tool.pytest.ini_options] pythonpath`
  ya no es necesario. Adoptarlo solo si se requiere fixture compartida.
- Añadir `tests/conftest.py` (hoy ausente) si se adopta pytest a gran escala.

**Criterio de aceptación**: PR verde/rojo reproducible; CI corre en cada push y el
pipeline queda **verde** al mergear (ver corrección de orden en el checklist).

---

## Fase 4 — Arquitectura / mantenibilidad

- **Descomponer** los módulos de mayor complejidad agregada: `commands.py` (54),
  `visitors/standards_visitor.py` (50), `utils/ast_utils.py` (44),
  `reporters/summary_reporter.py` (44), `fixer.py` (37), `validators.py` (36),
  `semantic.py` (36).
- [HECHO 2026-10-10] **Funciones sobre el gate**: `extract_runtime_imports_from_ast`,
  `apply_fixes` y `handle_analyze` refactorizadas (helpers extraídos); self-run con
  **0 funciones CC > 15**, desbloqueando el self-gate de Fase 3.
- [PENDIENTE] **Descomponer** los módulos de mayor complejidad agregada (`commands.py`,
  `standards_visitor.py`, `ast_utils.py`, `summary_reporter.py`, `fixer.py`,
  `validators.py`, `semantic.py`). Fuera del camino crítico del gate; se aborda en
  un refactor posterior.
- [PENDIENTE] **CLI en capas** (`main.py` → `cli/app.py` → `cli/commands/*` → `commands.py`):
  evaluar si los wrappers `cli/commands/*` aportan valor o fusionar con `commands.py`.
- [PENDIENTE] **Reporters** (`html/markdown/summary`) comparten agregación → base común.

---

## Fase 5 — Cobertura funcional — [DECIDIDO: PORTAR] [HECHO 2026-10-10]

Decisión del USER: **portar** los dominios huérfanos a `qgis-plugin-analyzer`.
Nota: las fuentes `.py` de patrones/anti-patrones **ya no existen** en
`ai-context-core` (solo quedan `.pyc` obsoletos), por lo que el port se hizo
**desde cero**; sí se reutilizó el cálculo de Halstead y la idea de
`optimization_checker`.

Implementado:
- `src/analyzer/utils/halstead.py`: métricas Halstead (vocabulary/length/volume/
  difficulty/effort), expuestas por módulo en `research_metrics.halstead`.
- `src/analyzer/visitors/patterns_visitor.py`: patrones de diseño (singleton/
  factory/observer/strategy/decorator) en `patterns` (informativos) y anti-patrones
  `GOD_OBJECT`, `SPAGHETTI_CODE`, `MAGIC_NUMBER`, `DEAD_CODE` como issues de
  severidad **info (Low)**, suprimibles con `# noqa`.
- Agregación en `aggregators`: `patterns` (mapa `patrón → module:name`) y
  `optimizations` (módulo grande / hotspot de complejidad) en el JSON.
- Regla registrada en el scope `all`/`architecture` de `CompositeVisitor`.
- Tests en `tests/test_patterns_visitor.py` (12). Self-run: `GOD_OBJECT` 1,
  `SPAGHETTI_CODE` 10, `MAGIC_NUMBER` 35; `quality_score` sin cambios (54.5).

---

## Fase 6 — Docs / DX

- Generar el catálogo de `RULES.md` desde el código (`list-rules`) para evitar deriva.
- `analysis_results/project_context.json` **ya** emite `analyzer_version`/`schema_version`;
  reformular esta tarea como "garantizar que los reporters no los pierdan" (los
  `project_context.json` de root/`src/` que sí carecían de ellos se retiran en Fase 0).
- Documentar el contrato de salida y el flujo de CI en un fichero **existente**
  (`docs/DEVELOPMENT_LOG.md` o `docs/development/DEVELOPMENT_LOG.md`); `docs/DEVELOPMENT.md` **no existe**.

---

## Orden de ejecución (checklist)

1. [x] Fase 0 — `git rm --cached` + `.gitignore` + borrar `migration/` (`e1fe47c`).
2. [x] Fase 3a — `ruff format .` (N1) + `ci.yml` ruff/mypy/pytest + `pythonpath` (`6a93bf5`).
3. [x] Fase 1.2 — ruff audit robusto (`0b0d4ec`).
4. [x] Fase 1.1 — `# noqa` transversal (`f26608c`).
5. [x] Fase 1.3 — normalización de paths (`f925bfd`).
6. [x] Fase 2.1 — workers configurables + batching (`662d3bb`); 2.2 caché **diferido**.
7. [x] Fase 4 — CC de las 3 funciones > 15 bajado a 0 violaciones (`88e927c`);
   descomposición de módulos/reporters y unificación CLI **pendiente**.
8. [ ] Fase 3b — self-gate `--max-cc 15` + cobertura (`pytest-cov`) [este commit].
9. [x] Fase 5 — PORTAR patrones/anti-patrones/Halstead/optimizaciones [hecho].
10. [ ] Fase 6 — docs/DX.
11. [ ] Cierre: `/close-session` + release `v1.15.0` (`/release-package`).

## Riesgos

- `git rm --cached` sobre `analysis.log`/`.coverage` rompe flujos locales que los lean;
  mitigación: documentar y regenerarlos en CI.
- El opt-out `# noqa` transversal puede silenciar hallazgos legítimos; mitigación:
  exigir el código explícito (`# noqa: CODE`) y mantener `# noqa` desnudo solo donde ya
  se usa (i18n).
- Portar patrones/anti-patrones añade superficie de falsos positivos; mitigación:
  severidad informativa (Low) y opt-out por regla.
- Cambiar `max_workers` por defecto altera uso de memoria en CI; mitigación:
  default `min(4, max(1, cpu-1))` (nunca supera el techo 4).
- Activar el self-gate `--max-cc 15` antes de la descomposición (Fase 4) deja el CI
  rojo y empuja a desactivarlo; mitigación: orden Fase 3a (sin gate) → Fase 4 →
  Fase 3b (con gate).
- `chunksize`/batching es un refactor, no un añadido trivial (`submit` → `map`);
  mitigación: tratarlo como tarea propia dentro de Fase 2 con tests de progreso.

## Aprobación

- Requiere aprobación explícita del USER (rol @architect) antes de escribir código.
- `/ia-critic` ejecutado (2026-10-10): veredicto **FAILED** → hallazgos M1–M10/O1–O10
  incorporados en esta revisión. Re-ejecutar antes de `/build-feature` tras la
  aprobación.
