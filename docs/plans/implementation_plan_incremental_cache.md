# Plan de Implementación: Caché Incremental por Hash de Contenido (Fase 2.2)

> **Estado**: propuesto — revisión 2 (corrige los defectos D1–D4 del `/ia-critic`
> 2026-10-11); pendiente de re-critic y aprobación del USER.
> **Meta**: acelerar análisis repetidos reutilizando el resultado por-fichero
> cuando el contenido **y** la configuración no han cambiado, con invalidación
> real y un opt-out `--no-cache`.
> Origen: `docs/plans/implementation_plan_repo_hygiene_and_hardening.md` §2.2
> (diferido a plan propio) y `.agent-state/task.md` id 4.3.

## 0. Evidencia medida (2026-10-11)

- No existe caché por-fichero: `scanner.analyze_module_worker(cached_data=...)`
  (`scanner.py:107`) es un parámetro **huérfano** (nunca se lee).
- La única "caché" es el artefacto de salida `analysis_results/project_context.json`
  que lee `summary` (staleness por `analyzed_at` con fallback a `mtime`,
  `utils/stale_cache.py:34-35`).
- Pipeline: `engine.run` → `parallel_analysis.run_parallel_analysis` (pool por chunks)
  → `scanner.analyze_chunk_worker` → `analyze_module_worker` (AST + visitors por fichero).
- `_apply_config_overrides` **solo** lo llama `handle_analyze` (`commands.py:107`);
  `handle_security` (`commands.py:281-309`) **no** lo llama (por eso `--strict` ya es
  un no-op en `security`). Relevante para D1.
- Orden no determinista (pre-existente): la salida usa `as_completed`
  (`parallel_analysis.py:75`); `optimizations` (`aggregators.py:180-209`) depende del orden,
  y `suggestions[:30]` está truncado. Relevante para D3.

## 1. Diseño

### 1.1 Nuevo módulo `src/analyzer/module_cache.py`

- `CACHE_SCHEMA = 1`, `CACHE_FILENAME = ".analyzer_cache.json"`.
- `file_content_hash(path) -> str`: `sha256` de los **bytes** del fichero.
- `analyzer_fingerprint() -> str` (**D2**): anclado al directorio del paquete, NO a
  `src/analyzer` relativo al CWD: `pathlib.Path(__file__).resolve().parent.rglob("*.py")`,
  excluyendo `__pycache__`, **ordenado** por `relpath`; `sha256` sobre `(relpath, sha256(content))`.
  Funciona con CWD arbitrario y con instalación en `site-packages`.
- `cache_signature(analyzer_version, *, project_path, rules_config, scope,
  include_content, project_type) -> str`: `sha256` de
  `analyzer_version + CACHE_SCHEMA + analyzer_fingerprint + project_path(resuelto) +
  rules_config (json sort_keys) + scope + include_content + project_type`.
  El `project_path` resuelto (**obs. del critic**) evita *cache poisoning* cuando dos
  proyectos comparten `--output`.
- `class ModuleCache`:
  - `__init__(path, signature)`, `load()`, `get(rel_path, content_hash)`,
    `put(rel_path, content_hash, result)`, `save()`.
  - Formato: `{"schema": 1, "analyzer_version": "…", "signature": "…",
    "entries": {"<rel>": {"hash": "…", "result": {…}}}`.
  - `load()` descarta la caché (queda vacía) si falta el fichero, está corrupta o
    `schema`/`signature` no coinciden.
  - `save()` **reconstruye `entries` desde el conjunto de ficheros de esta ejecución**
    (poda entradas de ficheros borrados/renombrados — obs. O-2 del critic).
  - Usa el `logger` de `qgis_analyzer` (nunca `print`) — pureza de stdout bajo `--json`.

### 1.2 Integración en `parallel_analysis.run_parallel_analysis`

Nueva firma: `run_parallel_analysis(..., cache: ModuleCache | None = None)`.

1. En el **proceso padre**: para cada fichero calcular `rel_path` (reutilizando
   `scanner._get_relative_path` para no duplicar lógica — obs. del critic) +
   `file_content_hash`; los aciertos (`cache.get`) se reutilizan; **solo los fallos**
   se envían al pool (**D-misses**).
2. `ProgressTracker(len(misses))` (no `len(files)`) para no mostrar un progreso falso;
   si `misses` está vacío, **se omite el pool** por completo.
3. Fusionar y **ordenar `modules_data` por `path`** (**D3**) → salida determinista que
   hace la caché transparente (y corrige además la no-determinación pre-existente).
4. `cache.put(...)` por cada resultado nuevo; `cache.save()` al final.
5. `cache is None` (`--no-cache`) → comportamiento actual (todo al pool, nada se guarda).

*Nota*: los ficheros fallidos (resultado `None`) no se cachean.

### 1.3 Motor

- `ProjectConfig.cache: bool = True`; `__init__` lee `raw_config.get("cache", True)`.
- `ProjectAnalyzer._build_cache(scope) -> ModuleCache | None`: se invoca en
  `_run_parallel_analysis` (después de los overrides de config, dentro de `run()`),
  construye el `ModuleCache` en `self.output_dir / CACHE_FILENAME` con la
  `cache_signature`, o devuelve `None` si `config.cache` es False.
- `_run_parallel_analysis` pasa la caché a `run_parallel_analysis`. El `GraphCommand`
  (`cli/commands/graph.py:61`) queda cubierto por el default keyword-only (usa caché).

### 1.4 CLI / config

- Flag `--no-cache` en `analyze` **y** en `security` (`cli/commands/security.py`).
- **D1**: añadir `_apply_config_overrides(analyzer, args)` en `handle_security` **antes**
  de `analyzer.run()` (además de `analyze`). Esto también arregla el `--strict` muerto
  en `security` (incidental).
- `_apply_config_overrides`: `if getattr(args, "no_cache", False): replace(..., cache=False)`.
- Clave `cache` del profile (`[tool.qgis-analyzer.profiles.<p>]`).

### 1.5 Limpieza

- Eliminar el parámetro huérfano `cached_data` de `analyze_module_worker`; justificado
  con `grep` en `src/` **y** `tests/` (lección 2026-10-10): los tests llaman con 2
  posicionales (`test_path_normalization.py:20,27`, `test_high_complexity.py:33`).

### 1.6 Ubicación del almacén y exclusión (**D4**)

- Fichero: `<output_dir>/.analyzer_cache.json` (por defecto `analysis_results/`, ya ignorado).
- Añadir `".analyzer_cache.json"` a `DEFAULT_EXCLUDE` (`utils/path_utils.py`) para que
  **nunca** se cuente como fichero del proyecto con `--output` personalizado.
- Añadir `.analyzer_cache.json` a `.gitignore` (defensa en profundidad).

## 2. Matriz de invalidación

| Cambio | Efecto |
| :--- | :--- |
| Contenido de un fichero | Re-analiza **ese** fichero (hash distinto). |
| Código del analizador (paquete `analyzer/**`) | `analyzer_fingerprint` cambia ⇒ caché completa descartada. |
| `analyzer_version` / `CACHE_SCHEMA` | Caché descartada. |
| `rules_config` / `scope` / `include_content` / `project_type` | `signature` cambia ⇒ descartada. |
| `project_path` resuelto distinto | `signature` cambia ⇒ descartada (evita mezcla entre proyectos). |
| Fichero añadido/eliminado | Entrada ausente = fallo; entradas sobrantes se ignoran. |
| Flag `--no-cache` | No se lee ni se escribe caché. |

## 3. Tests

- `tests/test_module_cache.py`: estabilidad del hash; invalidación por `signature`
  (versión, fingerprint, project_path, scope, include_content); round-trip `save`/`load`;
  fichero corrupto/JSON inválido → caché vacía.
- `tests/test_incremental_cache.py`:
  - Segunda ejecución sin cambios reutiliza (espía `analyze_chunk_worker` ⇒ 0 llamadas).
  - Editar un fichero ⇒ solo ese se re-analiza.
  - `--no-cache` ⇒ nunca reutiliza (y no escribe caché).
  - **D3**: `project_context.json` de la 2ª ejecución == 1ª **salvo `analyzed_at`**
    (posible gracias a la ordenación determinista de §1.2). Test **in-process** sobre
    un proyecto **genérico** temporal (sin red), para evitar la no-determinación
    residual de `set()` (`docstring_styles`) y `url_status` (obs. O-1 del critic).
- `tests/test_cli_commands.py`: `security --no-cache` ⇒ `analyzer.config.cache is False`
  (cubre D1).

## 4. Riesgos y mitigaciones (actualizado)

- **Lógica cambia sin subir versión** → `analyzer_fingerprint` anclado al paquete (D2).
- **Caché entre proyectos con `--output` compartido** → `project_path` en la `signature`.
- **Caché contada como fichero del proyecto** → `DEFAULT_EXCLUDE` + `.gitignore` (D4).
- **Orden no determinista** → `modules_data` ordenado por `path` (D3).
- **Tamaño del fichero de caché** → vive en `output_dir` (ignorado), borrable.
- **Doble lectura** de ficheros cambiados (padre para hash + worker) → aceptable.
- **Signature thrash** entre `analyze security` (scope=security) y `security` (scope=all)
  → documentado; invalida mutuamente (correcto, no óptimo).
- **Pureza de stdout** bajo `--json` → el módulo de caché solo usa `logger`.

## 5. Verificación

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy src/
uv run python -m pytest tests/ -q
uv run qgis-analyzer analyze . --max-cc 15
```

**Criterio de aceptación**: 2ª ejecución sin cambios reutiliza el 100% de módulos;
editar un fichero re-analiza solo ese; `--no-cache` desactiva todo; salida idéntica
(salvo `analyzed_at`).

## 6. Fuera de alcance

- Caché a nivel de proyecto (scores/agregación) — solo se cachea el análisis por-fichero.
- Cacheado del audit de Ruff (subprocess) — se ejecuta siempre.
