# Plan de Implementación: Generalizar el Analizador (i18n AST + Gate CC)

> **Estado**: aprobado para implementación
> **Meta**: que `qgis-plugin-analyzer` analice correctamente **cualquier** plugin QGIS,
> no solo SecInterp. Portar la lógica madura (i18n por AST y gate de complejidad) de
> forma genérica y con un contrato de salida fiable para CI.

## 0. Decisiones resueltas

| Decisión | Resolución |
| :--- | :--- |
| ID de regla i18n | **Mantener `MISSING_I18N`** y reemplazar su heurística por lógica AST completa. |
| Floor de Python | **Subir a `>=3.11`**. `tomllib` pasa a ser stdlib garantizada; se elimina el parser TOML mínimo como bloqueante de arrays. |
| Implementación de referencia | Relocalizar `docs/plans/i18n_ast_rule.py` → `scripts/upstream/i18n_ast_rule.py` y portar su lógica al visitor. |

Racional de "mantener `MISSING_I18N`": evita tocar el mapa de scope en
`src/analyzer/engine.py:409`, `src/analyzer/visitors/base.py:79`, los reportes y los
tests existentes. Crear `UNTRANSLATED_STRING` añade superficie sin beneficio.

Racional de "subir a 3.11": elimina la bifurcación `tomllib`/`_minimal_toml_load` en
`src/analyzer/utils/config_utils.py`, que hoy es incapaz de parsear arrays en
Python 3.9/3.10 y haría que la config del i18n (`extra_ignore_calls`,
`extra_exact_ignores`) se perdiera silenciosamente.

---

## Fase 0 — Contrato de salida (bloqueante para CI)

Los consumidores del JSON necesitan un shape estable y ligero antes de añadir
reglas. Hacer **antes** de Fase 1 y 2.

### 0.1 `schema_version` + `analyzer_version`

- `src/analyzer/aggregators.py` → `build_analysis_results()` (~línea 165): añadir
  `"schema_version": 1` y `"analyzer_version": __version__`.
- Importar `__version__` desde `src/analyzer/__init__.py:59`.

### 0.2 `--include-content` (off por defecto)

- Nuevo campo `include_content: bool = False` en `ProjectConfig`
  (`src/analyzer/engine.py:63`).
- `src/analyzer/scanner.py:161`: escribir `"content": content` **solo** si
  `include_content` está activo.
- Threading: `engine.py:196` (`shared_context`) → `analyze_module_worker` → resultado.
- Verificar que `audit_qgis_standards` sigue funcionando sin `content`: ya tiene
  fallback `_try_read_module_file` (`scanner.py:283`).

**Efecto esperado**: `project_context.json` de ~468 KB a ~20-30 KB y sin leak de fuente.

### 0.3 `--json` en `analyze` + ruta de salida canónica

- Flag `--json` en `src/analyzer/cli/commands/analyze.py` (o `add_common_args` en
  `base.py:55`).
- `src/analyzer/commands.py` → `handle_analyze()`: si `--json`, volcar
  `project_context.json` a stdout tras el run.
- El engine ya resuelve `output_dir` con `.resolve()` (`engine.py:90`); documentar
  la ruta canónica en la salida.

### 0.4 Warning de directorio de salida legacy

- En `src/analyzer/cli/base.py:91` (`setup_output_dir`) y/o `app.py:100`
  (`_setup_logging`): detectar `json/project_context.json` (legacy) y emitir warning
  de migración.

---

## Fase 1 — Regla i18n AST (`MISSING_I18N`)

### 1.1 Relocalizar referencia

- `git mv docs/plans/i18n_ast_rule.py scripts/upstream/i18n_ast_rule.py`
  (arregla el enlace roto del plan `upstreaming_qgis_analyzer.md` §3.1).

### 1.2 Portar la lógica al visitor

Reemplazar en `src/analyzer/visitors/i18n_visitor.py`:
- `is_translatable_string()` (línea 158) y `IGNORED_I18N_FUNCTIONS` (línea 31) por:
  - `I18nAstVisitor` / `collect_docstring_lines` / `is_technical_string`.
  - `DEFAULT_SAFE_CALL_SUFFIXES`, `DEFAULT_TECHNICAL_PATTERNS`,
    `DEFAULT_SAFE_EXACT_STRINGS` (del script `i18n_ast_rule.py`).
- Mantener el `# no-i18n` como marca de exclusión inline.

### 1.3 Threading de líneas fuente (soporte de comentarios)

Hoy el analizador **ignora los comentarios** por completo (grep confirma 0
ocurrencias de `no-i18n`/`noqa`). Para soportar la exclusión inline:

- Pasar `content`/`lines` desde `src/analyzer/scanner.py:145`
  (`QGISASTVisitor(rel_path, rules_config=..., scope=...)`) → `CompositeVisitor.__init__`
  → `I18nVisitor`.
- En `visit_Constant`, leer `lines[lineno-1]` y saltar si contiene `# no-i18n` o `# noqa`.

### 1.4 Configuración por proyecto

- Bajo `[tool.qgis-analyzer.profiles.<p>.rules.MISSING_I18N]`:
  - `extra_ignore_calls` (array), `extra_exact_ignores` (array).
- Defaults = `DEFAULT_*` genéricos del script (sin entradas SecInterp-específicas).
- Con floor 3.11, `load_profile_config` (`config_utils.py:96`) usa `tomllib` nativo
  y parsea arrays correctamente. Eliminar `_minimal_toml_load` (Fase 3).

### 1.5 Verificar mapa de scope

- `MISSING_I18N` ya está en `engine.py:409` y `base.py:79`; no requiere cambios al
  mantener el ID.

---

## Fase 2 — Gate de complejidad (`--max-cc N`)

### 2.1 Flag + handler

- Flag `--max-cc N` (default off) en `src/analyzer/cli/commands/analyze.py` +
  `base.py` (common args).
- `src/analyzer/commands.py` → `handle_analyze()`: tras el run, aplicar gate.

### 2.2 Implementación

```python
def _enforce_max_cc(modules_data, max_cc):
    violations = []
    for mod in modules_data:
        for func in mod.get("functions", []):
            if func.get("complexity", 0) > max_cc:
                violations.append((mod["path"], func["name"], func["line"], func["complexity"]))
    if violations:
        violations.sort(key=lambda v: v[3], reverse=True)
        for path, name, line, cc in violations:
            print(f"  - {path}:{line} -> {name} (CC={cc})")
        return False
    return True
```

- `functions[].complexity` ya existe (`src/analyzer/utils/ast_utils.py:53`).
- `sys.exit(1)` si hay violaciones.
- Exponer en `--json`: `"cc_gate": "PASS|FAIL"` + `"cc_violations": [...]`.

> Nota: el CC reportado incluye penalización por densidad (`ast_utils.py:47`, `×1.5`).
> Es coherente con `summary --by functions`; documentar que el gate usa ese valor.

---

## Fase 3 — Bump Python a 3.11

### 3.1 `pyproject.toml`

- `requires-python = ">=3.11"` (línea 6).
- Classifiers: eliminar `3.9`, `3.10` (líneas 25-26); mantener `3.11`-`3.13`.
- `tool.mypy python_version = "3.11"` (línea 63).
- `tool.ruff target-version = "py311"` (línea 72).

### 3.2 Eliminar parser TOML mínimo

- `src/analyzer/utils/config_utils.py`: eliminar `_minimal_toml_load` y el fallback
  `try: import tomllib / except ImportError`, dejando `tomllib` como única vía.
- Ajustar `src/analyzer/utils/__init__.py:12` (ya exporta `_minimal_toml_load`).

### 3.3 CI/entorno

- Actualizar `.github/workflows/release.yml` (matriz de Python) si referencia 3.9/3.10.
- Actualizar `agentic_framework_guide.md` / docs de instalación si mencionan la versión.

---

## Fase 4 — Pruebas

- **Golden**: correr el nuevo `I18nVisitor` sobre corpus SecInterp → validar FP → 0
  (necesita fixture externo; documentar el procedimiento).
- **Sintéticos** (ampliar `tests/test_i18n_heuristics.py`):
  - CSS/HTML, format strings, docstrings multilínea, `QCoreApplication.translate()`,
    `super().__init__(translate(...))` → 0 violaciones.
  - String user-facing real → 1 violación.
  - `# no-i18n` inline → 0 violaciones.
- **Gate CC**: fixture con función CC 15 → exit 1; CC ≤ 10 → exit 0.
- **Back-compat**: `--json` y `summary` mantienen el mismo shape de `project_context.json`.

---

## Fase 5 — Docs / limpieza

- Marcar `docs/qgis-analyzer-i18n-improvement.md` como superado por este plan.
- Actualizar `docs/plans/upstreaming_qgis_analyzer.md` (enlace a la referencia
  relocalizada y nota de decisión de ID).
- Documentar (no ejecutar) la migración de SecInterp §8 del plan original.

---

## Orden de ejecución (checklist)

1. [ ] Fase 0.1 — `schema_version` + `analyzer_version`.
2. [ ] Fase 0.2 — `--include-content`.
3. [ ] Fase 0.3 — `--json` + ruta canónica.
4. [ ] Fase 0.4 — warning legacy output dir.
5. [ ] Fase 3 — bump Python 3.11 + eliminar parser TOML mínimo.
6. [ ] Fase 1.1 — relocalizar referencia.
7. [ ] Fase 1.2/1.3/1.4 — portar visitor AST + threading líneas + config.
8. [ ] Fase 2 — gate `--max-cc`.
9. [ ] Fase 4 — pruebas (sintéticas + golden + CC + back-compat).
10. [ ] Fase 5 — docs/limpieza.

## Riesgos

- La eliminación del parser TOML mínimo rompe Python <3.11; mitigado por el bump
  explícito de `requires-python` y el ajuste de CI (Fase 3.3).
- La generalización de `TECHNICAL_PATTERNS` puede requerir afinado para otros
  plugins; mitigación: `extra_ignore_calls`/`extra_exact_ignores` configurables +
  `.analyzerignore`.
- Pérdida de precisión SecInterp al generalizar (`SAFE_EXACT_STRINGS` específicos);
  mitigación: `extra_exact_ignores` configurable por proyecto.
