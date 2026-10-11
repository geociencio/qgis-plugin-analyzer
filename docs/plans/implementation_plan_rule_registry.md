# Plan de Implementación: Registro Unificado de Reglas + `RULES.md` Autogenerado (Fase 6)

> **Estado**: propuesto — revisión 2 (corrige las 7 correcciones bloqueantes del
> `/ia-critic` 2026-10-11); pendiente de re-critic y aprobación del USER.
> **Meta**: un **registro único de reglas** como fuente de verdad de los ids
> (regex + AST/visitor + seguridad + secretos + patrones), del que se deriven
> `list-rules` y `RULES.md` (autogenerado), eliminando el drift manual.
> Origen: `docs/plans/implementation_plan_repo_hygiene_and_hardening.md` §Fase 6,
> `.agent-state/task.md` id 4.2 y `docs/reports/ANALYSIS_REPORT.md:32,61`.

## 0. Evidencia medida (2026-10-11)

- `list-rules` (`commands.py:244-251`) solo lista las **7** reglas regex de `get_qgis_audit_rules()`.
- `RULES.md` es **manual** y lo declara (líneas 5-8).
- **Conjunto emitido = 51 ids distintos** (unión con deduplicación):
  - 32 literales `_report_issue("ID", …)` en `visitors/*.py`;
  - 3 claves de `QT6_REMOVED_NAMES` (`qt_transition_visitor.py:10`), emitidas dinámicamente;
  - 7 regex (`rules/qgis_rules.py`);
  - 6 de seguridad (`B102,B301,B307,B602,B608,HARDCODED_SECRET`) devueltos dentro de funciones;
  - 5 de secretos (`PATTERNS` keys + `HIGH_ENTROPY`, `secrets.py:25-30,64`).
  - **Solape** regex↔visitor: `UNSAFE_SUBPROCESS` y `BLOCKING_NETWORK_CALL` (2 ids) → 32+3+7+6+5−2 = **51**.
- **17 ids emitidos NO están documentados** en `RULES.md` (hay que redactarlos):
  `LEGACY_GDAL_IMPORT, LEGACY_SIGNAL_SLOT, MISSING_DOCSTRING, MISSING_TYPE_HINTS,
  NON_PYTHONIC_LOOP, PYQT5_IMPORT, B102, B301, B307, B602, B608, HARDCODED_SECRET,
  AWS_KEY, GOOGLE_API_KEY, TWILIO_KEY, GENERIC_SECRET, HIGH_ENTROPY`.
- `SCOPE_RULES` (`rules/scopes.py`) tiene 37 ids; **14 emitidos NO tienen scope**
  (`DEAD_CODE, GOD_OBJECT, HIGH_COMPLEXITY, LEGACY_SIGNAL_SLOT, MAGIC_NUMBER,
  MISSING_DOCSTRING, MISSING_TYPE_HINTS, POTENTIAL_MISSING_SLOT, SPAGHETTI_CODE` +
  5 solo-regex: hoy quedan fuera de todo scope).
- **Severidad (hallazgo)**: `BaseVisitor._get_severity` (`base.py:86-101`) mapea
  `error/warning/info → high/medium/low`, con default `"warning"`; como ningún
  profile define `rules`, **toda issue de AST sale como `medium` en runtime**. La
  severidad de `RULES.md` es por tanto **descriptiva** y no coincide con runtime.
  `_get_severity` **nunca** emite `info`.
- `CompositeVisitor._active_visitors` (`composite_visitor.py:63-89`) es un **segundo**
  mapa scope→visitor (fuente de drift independiente de `SCOPE_RULES`).

## 1. Diseño

### 1.1 Catálogo unificado `src/analyzer/rules/registry.py` (SSoT, sin dependencias)
- `@dataclass(frozen=True) class Rule`: `id`, `severity` (`high|medium|low`; **sin `info`**),
  `category`, `description`, `recommendation`, `scopes: tuple[str, ...]`,
  `sources: tuple[str, ...]` (**multi-origen**, p.ej. `UNSAFE_SUBPROCESS` =
  `("regex", "visitor")`), `emitted: bool = True`.
- `RULE_CATALOG: dict[str, Rule]` con las **51** reglas emitidas (+ filas
  documentales necesarias). El módulo importa **solo stdlib** (dataclasses) → seguro
  de importar desde `visitors/base.py`.
- `INFORMATIONAL: list[...]` para la sección "no-issue" (`patterns`, `optimizations`,
  `halstead`). **`SIGNAL_LEAK` se modela aparte** (fila tachada, `emitted=False`) para
  reproducir `RULES.md:31` — no va en INFORMATIONAL (está en la tabla de §3).
- Export ligero `KNOWN_RULE_IDS: frozenset[str]` para `_report_issue`.
- Helpers: `get_rule(id)`, `get_rules()` (**proyección `emitted=True`**, las 51),
  `rules_for_scope(scope)`, `categories()`.
- **La severidad del catálogo es descriptiva/documental** (no la consume
  `_get_severity`); el test de paridad es una **guarda de drift catálogo↔`qgis_rules.py`**
  para las 7 regex (no afirma paridad con la severidad *emitida*, que en runtime se
  remapea a `medium`).
- Autoría: 34 filas desde `RULES.md` + **17 nuevas** (listadas en §0).

### 1.2 `SCOPE_RULES` derivado del catálogo (sin cambio de comportamiento)
- `rules/scopes.py` proyecta `rule.scopes`; los **14 ids sin scope mantienen
  `scopes=()`** (no se les asigna scope "natural", para no cambiar el filtrado).
- **Test de paridad exacto**: compara con un **snapshot hardcodeado** de los
  `{scope: set(ids)}` actuales (igualdad exacta, no subconjunto).
- Nota documentada: `CompositeVisitor._active_visitors` sigue siendo un segundo mapa;
  unificarlo queda **fuera de alcance**.

### 1.3 `list-rules` lista todas las reglas
- `handle_list_rules` usa el catálogo agrupado por `category`
  (`- [SEVERITY] ID: description`). Nueva opción `list-rules --format {text,markdown}`
  (default `text`), reutilizando el renderer de §1.4.
- **Test**: el conjunto de ids impresos == `{r.id for r in get_rules()}`.

### 1.4 `RULES.md` autogenerado y determinista
- `scripts/generate_rules_md.py` (adapter, como `scripts/sync_metrics.py`) renderiza
  `RULES.md` desde el catálogo:
  - reproduce las secciones y numeración actuales (`## 1.`…`## 9.`, incluida `## 7.1`);
    la prosa de §9 se reescribe con el vocabulario `high|medium|low` (sin `info`);
  - conserva la fila **tachada** `SIGNAL_LEAK` y la tabla "Informational (not issues)";
  - **reescribe la nota de cabecera** (elimina "follow-up (Fase 6)") y añade
    "generated by scripts/generate_rules_md.py — do not edit".
- **Tests**: (a) determinismo (render 2× ⇒ bytes idénticos); (b) sincronía
  (render == `RULES.md`); (c) `--check` falla si hay drift.

### 1.5 Ids de seguridad y secretos enumerables
- `security_check(node_type, rule_ids=("B102","B307"))` + `SecurityRegistry.rule_ids()`
  (`security_checker.py`); actualizar las **5** funciones de `security_rules.py`.
- `SecretScanner.rule_ids()` (claves de `PATTERNS` + `HIGH_ENTROPY`).
- **Test**: `SecurityRegistry.rule_ids()` **no vacío** (lección 2026-10-10: registro
  poblado por side-effect de import).

### 1.6 Guardas anti-drift `tests/test_rule_registry.py`
- **Esquema/unicidad**: severidades ∈ {high,medium,low}, categorías válidas, ids únicos.
- **Paridad SCOPE_RULES** exacta (§1.2) y **paridad de severidad** con las 7 regex.
- **Cobertura bidireccional**:
  `extracted == {r.id for r in RULE_CATALOG.values() if r.emitted}`, donde `extracted` =
  (AST-scan de literales primer-arg de `_report_issue` sobre **todo `src/analyzer`**)
  ∪ `QT6_REMOVED_NAMES` keys ∪ ids regex ∪ `SecurityRegistry.rule_ids()`
  ∪ `SecretScanner.rule_ids()`.
- **Allowlist de emisiones no-literal**: toda llamada a `_report_issue` cuyo primer
  arg **no** sea un literal debe estar en un **allowlist explícito**
  (`{qt_transition_visitor.py:74, :132}`); si aparece una nueva → **falla** (evita drift
  silencioso).
- **`RULES.md` sincronizado** y render determinista (§1.4).
- **Canal de seguridad**: además de `SecurityRegistry.rule_ids()`, el test extrae por AST
  los literales `id="…"` de `security_rules.py` (incluida la ternaria `B102/B307`,
  `security_rules.py:30`) y exige que coincidan con `rule_ids()`.
- **Guarda de runtime**: test de que `_report_issue` avisa **una sola vez** por id desconocido.

### 1.7 Guarda en runtime + back-compat
- `BaseVisitor._report_issue` avisa **una sola vez por id desconocido** (set a nivel de
  módulo) usando `KNOWN_RULE_IDS` (import ligero, sin arrastrar `secrets`/`security_checker`).
- Se mantienen `get_qgis_audit_rules()`, `SCOPE_RULES` y **todos los ids estables**.
- Actualizar `CONTRIBUTING.md:50` (dónde se declaran las reglas → `rules/registry.py`),
  `:51` y `:87` para reflejar que `RULES.md` es **generado**.

## 2. Riesgos y mitigaciones

- **17 ids requieren redacción nueva** → presupuestado en §1.1.
- **Severidad doc ≠ runtime** (pre-existente) → documentado como descriptivo; **no** se
  cambia el runtime (fuera de alcance).
- **Drift-test frágil** → allowlist explícita de emisiones dinámicas + scan de todo `src/analyzer`.
- **`CompositeVisitor` segundo mapa** → documentado; unificar es follow-up.
- **`SCOPE_RULES`** → 14 ids con `scopes=()` + paridad exacta snapshot.

## 3. Verificación

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy src/                      # (scripts/ fuera de mypy, como hoy)
uv run python -m pytest tests/ -q
uv run qgis-analyzer list-rules
uv run python scripts/generate_rules_md.py --check
uv run qgis-analyzer analyze . --max-cc 15
```

**Criterio de aceptación**: `list-rules` y `RULES.md` listan **las 51** reglas desde el
catálogo; `RULES.md` regenerable/determinista y sincronizado; `SCOPE_RULES` **idéntico**
al actual; `MISSING_DOCSTRING`/`MISSING_TYPE_HINTS` etc. dejan de faltar; suite y
self-gate en verde.

## 4. Fuera de alcance

- Reescribir visitors para referenciar constantes del catálogo (se conservan literales).
- Alinear la severidad de runtime con `RULES.md`.
- Unificar `CompositeVisitor._active_visitors` con `SCOPE_RULES`.
