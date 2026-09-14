# Upstreaming Plan: SecInterp scripts → qgis-plugin-analyzer

## 1. Premisa

SecInterp y qgis-plugin-analyzer comparten autor. El analizador es la
herramienta reutilizable de análisis estático para plugins QGIS; SecInterp
acumuló lógica más madura en dos áreas — i18n por AST y gate de complejidad —
que hoy viven como scripts ad-hoc (`scripts/verify_i18n_hygiene.py`,
`scripts/check_cc.py`).

Este plan traslada esa madurez al analizador para que **cualquier** plugin
QGIS se beneficie, y luego retira los scripts duplicados de SecInterp.

## 2. Alcance

| Origen (SecInterp) | Destino (qgis-analyzer) | Acción |
| :--- | :--- | :--- |
| `verify_i18n_hygiene.py` | `visitors/i18n_visitor.py` | **Reemplazar** la heurística `is_translatable_string()` por el enfoque AST completo |
| `check_cc.py` | `analyzer/commands.py` (flag nueva en `analyze`) | **Añadir** gate `--max-cc N` reutilizando `functions[].complexity` ya calculado |
| `security_scan.py`, `sync_metrics.py`, scripts agénticos | — | **No subir** (orquestación multi-tool y sistema `.agent/`, fuera del alcance del analizador) |

## 3. Gap analysis

### 3.1 i18n

`I18nVisitor.is_translatable_string()` genera 72 false positives en SecInterp.
Causa raíz: solo excluye rutas, `_`, `.`, palabras técnicas sueltas y
mayúsculas, pero **no** distingue CSS/HTML, format specifiers, colores,
extensiones, keys de QSettings ni docstrings multilínea.

El enfoque de SecInterp (`scripts/verify_i18n_hygiene.py`) añade:

- `_collect_docstring_lines()` — excluye docstrings (incluidos multilínea vía
  `end_lineno`).
- `TECHNICAL_PATTERNS` (24 regex) — CSS, HTML, `*.png`, `#hex`,
  `field=wkt:wkt`, tipos de geometría, `%.2f`, etc.
- Call-stack de `SAFE_CALL_SUFFIXES` (sufijos `tr`/`translate`/`debug`/…) —
  evita el falso positivo de `QCoreApplication.translate()`.
- Gate "parece user-facing" (`has_spaces and has_alpha`).

La implementación de referencia portable vive en
[`scripts/upstream/i18n_ast_rule.py`](../../scripts/upstream/i18n_ast_rule.py).

### 3.2 Complejidad

`scanner.py` ya calcula `functions[].complexity`; solo falta exponerlo como
gate con exit code para CI.

## 4. Prerrequisitos (contrato de salida) — hacer PRIMERO

Bloqueantes para consumir el JSON de forma fiable:

1. `project_context.json` → añadir `"schema_version"` y `"analyzer_version"`.
2. Hacer opcional `modules[].content` (`--include-content`, off por defecto) →
   de 468 KB a ~20-30 KB y elimina el leak de fuente.
3. Canonicalizar la ruta de salida (resolver `./analysis_results` relativo al
   proyecto; exponerla) + flag `--json` en `analyze` para CI.
4. Warning de directorio de salida obsoleto (detectar `json/project_context.json`
   legacy).

## 5. Integración A — Regla i18n AST (`UNTRANSLATED_STRING`)

1. Portar `I18nAstVisitor` + `collect_docstring_lines` + `is_technical_string`
   de `scripts/upstream/i18n_ast_rule.py` a `visitors/i18n_visitor.py`.
2. Generalizar los acoplamientos SecInterp:
   - Paths → usar el discovery de archivos del analizador (ya respeta
     `.analyzerignore`).
   - `SAFE_CALL_SUFFIXES` / `SAFE_EXACT_STRINGS` → configurables vía
     `pyproject.toml` bajo
     `[tool.qgis-analyzer.profiles.<p>.rules.UNTRANSLATED_STRING]`
     (`extra_ignore_calls`, `extra_exact_ignores`), con defaults genéricos.
   - Sin entradas SecInterp-específicas (`SecInterpError`, `ValidationError`,
     `PerformanceTimer`, `track`, strings de preview).
3. Mantener `# no-i18n` como marca de exclusión inline.
4. Nueva regla con id `UNTRANSLATED_STRING` (o `MISSING_I18N` con flag
   `--ast-precise`); severidad `medium`; alcance `i18n`/`all`.
5. Back-compat: mantener el `MISSING_I18N` heurístico como fallback opcional.

## 6. Integración B — Gate de complejidad

```python
# analyzer/commands.py — handle_analyze()
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

Comportamiento:
- `analyzer/commands.py` → flag `--max-cc N` (default off) en `analyze`.
- Tras el run, aplicar `_enforce_max_cc` y `sys.exit(1)` si hay violaciones.
- Exponer en `--json` como `"cc_gate": "PASS|FAIL"` + `"cc_violations": [...]`.

## 7. Integración C (opcional) — artefactos obsoletos

Añadir heurística de "stale output dir" (detectar `json/project_context.json` u
otras ubicaciones legacy) con warning de migración — refuerza la lección de
`AGENT_LESSONS.md`.

## 8. Migración de SecInterp (documentada, no ejecutada)

Al publicar una versión del analizador con soporte:

1. `scripts/check_cc.py` → retirar (sustituido por
   `qgis-analyzer analyze --max-cc 10`).
2. `scripts/verify_i18n_hygiene.py` → retirar (sustituido por la regla
   `UNTRANSLATED_STRING`).
3. Actualizar `scripts/sync_metrics.py` (reemplazar llamadas a `check_cc.py`/
   `verify_i18n_hygiene.py` por la flag/JSON del analizador), `Makefile`,
   `.pre-commit-config.yaml`, `.agent/workflows/*` y el pre-push hook.
4. Actualizar `.agent/memory/agent_metrics.json` → `meta.tools` con la nueva
   versión del analizador.

## 9. Estrategia de pruebas

- **Golden files**: correr el nuevo `I18nVisitor` sobre el corpus SecInterp y
  validar que 72 FP → 0 (sin cambios de código).
- **Fixtures sintéticos**: archivos con CSS, HTML, format strings, docstrings
  multilínea, `QCoreApplication.translate()` → 0 violaciones; strings
  user-facing reales → 1 violación.
- **Gate CC**: fixture con función de CC 15 → exit 1; CC ≤ 10 → exit 0.
- **Back-compat**: `--json` y `summary` siguen reportando el mismo shape.

## 10. Riesgos y tradeoffs

- **Deriva**: subir la lógica introduce un ciclo de versiones (SecInterp
  dependerá de una versión mínima). Mitigación: versión mínima en `pyproject.toml`.
- **False positives en terceros**: la generalización puede requerir afinar
  `TECHNICAL_PATTERNS` para otros plugins. Mitigación: configuración por
  proyecto vía `pyproject.toml` + `.analyzerignore`.
- **Pérdida de precisión SecInterp**: al generalizar, algunos
  `SAFE_EXACT_STRINGS` específicos se perderán. Mitigación:
  `extra_exact_ignores` configurable.
