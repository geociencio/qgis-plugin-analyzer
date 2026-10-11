# Deep Analysis Report — qgis-plugin-analyzer v1.15.0

**Scope**: Dead code, duplication, complexity and optimization, with cross-tool boundary
guardrails for `ai-context-core` and `qgis-plugin-manager`.

**Source under analysis**: repository at `qgis_plugin_analyzer/`, commit `0d1f53b`,
`version = "1.15.0"` (57 modules, 8,634 LOC).

**Method / tooling** (no source changes):

| Tool | Purpose | Result |
| :--- | :--- | :--- |
| `ruff` 0.15.2 | lint + F-rules (unused/dead) | base config: **clean**; extended rules: 32 findings (mostly license-header `ERA001`, visitor `ARG002`) |
| `pylint` 4.0.7 | `R0801` duplicate code + design | **4** duplicate blocks; 20 design smells |
| `vulture` 2.14 | dead code | 3 @100%, 44 @60% (many false positives) |
| `radon` 6.0.1 | CC / MI | 15 functions rank **C**; no rank D+ |
| `pytest --cov` | coverage | 161 tests, **75 %** total; 2 packages at **0 %** |
| `grep` (reference check) | confirm usage | each candidate verified by references |

---

## 1. CRITICAL — Disconnected code, not dead code

`src/analyzer/security_rules.py` (129 lines) is the **only** module that registers the
Bandit-inspired checks, via the `@security_check` decorator writing into
`SecurityRegistry._checks`. **The module is never imported**, so the decorator never runs
and the registry stays empty. `SecurityVisitor` (aliased `QGISSecurityVisitor`) dispatches
exclusively through `SecurityRegistry.get_checks_for_node()` (`visitors/security_visitor.py:32`),
therefore **no AST security check executes**.

### Evidence

```
$ PYTHONPATH=src python -c "import analyzer.scanner as s; from analyzer.security_checker import SecurityRegistry as R; print(sum(len(v) for v in R._checks.values()))"
0
$ # after importing security_rules explicitly:
5
```

End-to-end probe — a file containing `eval`, `exec`, `os.system`, `pickle.loads`,
`yaml.load` and SQL-by-concatenation:

```
Security Health Score: 100.0/100
Total vulnerabilities detected: 0
```

Only `UNSAFE_SUBPROCESS` is ever produced, and by a *different* code path
(`standards_visitor._check_unsafe_subprocess`, `visitors/standards_visitor.py:201`), not by
the security registry.

### Impact

- Undetected: `exec`/`eval` (B102/B307), `pickle` (B301), `subprocess shell` (B602),
  SQL injection (B608), hardcoded-password assignment.
- The scope maps reference rule IDs that **no code emits** → phantom rules:
  `UNSAFE_YAML`, `UNSAFE_PICKLE`, `SQL_INJECTION`, `HARDCODED_PASSWORD`
  (`engine.py:481-487`, `visitors/base.py:82-88`).
- **Cross-tool**: `qgis-manage security` shells out to `qgis-analyzer security`
  (`qgis-plugin-manager/src/qgis_manager/cli/analyzer.py`), so the Manager inherits the
  same false negative.

### Recommendation (P0)

Do **not** delete `security_rules.py`. Wire the import side effect (e.g.
`from . import security_rules  # noqa: F401` in `security_visitor.py`), **or** converge the
two security engines on a single implementation. Add a regression test asserting
`len(SecurityRegistry._checks) > 0` and that `eval`/`pickle`/SQL produce a finding.

---

## 2. Confirmed dead code (references + 0 % coverage)

| File / symbol | LOC | Evidence | Action |
| :--- | ---: | :--- | :--- |
| `models/analysis_models.py` + `models/__init__.py` (`ModuleAnalysis`, `ProjectContext`) | 67 | 0 % coverage; only self-references; the real model is `ModuleAnalysisResult` TypedDict (`scanner.py:59`) | **Delete package `models/`** |
| `rules/modernization_rules.py::get_modernization_rules` | 33 | function body 0 %; only re-exported, no consumer | Delete or wire |
| `security_rules.py` | 129 | never imported | **Wire, do not delete** (§1) |
| `transformers.py::apply_transformation` (l.187) | ~5 | only `apply_transformation_to_content` is used | Delete |
| `fixer.py::get_all_handlers` (l.121) | ~5 | 0 references (incl. tests) | Delete |
| `cli/base.py::setup_output_dir` (l.91) | ~10 | 0 references | Delete |
| `validators.py::calculate_package_size` / `scan_for_binaries` (l.264/281) | ~35 | production-unused; only tests | Wire into compliance or move to test helpers |
| `scanner.py::analyze_module_worker(cached_data=…)` | – | `W0613`, parameter never used | Remove or relabel |
| `performance_utils.py:100 file_path`, `:157 frame`/`signum` | – | `W0613` / vulture | Prefix `_` |

Total dead ≈ **229 LOC (~2.7 %)** plus ~60 LOC in loose functions.

### Ruled out (vulture false positives)

`dataclass`/`TypedDict` fields, and every `leave_*` method (`leave_ClassDef`,
`leave_FunctionDef`, `leave_Call`): the latter are dispatched dynamically via
`BaseVisitor.exit_node` (`visitors/base.py:55-68`).

---

## 3. Duplication (broken single source of truth)

1. **`scope → rule_ids` map duplicated**
   `engine.py:479-518` (`_filter_issues_by_scope`) and `visitors/base.py:76-128`
   (`_should_report`) encode the same 5-scope mapping. Adding a rule to one place and not
   the other silently desynchronizes scope filtering.
   → Extract a module-level `SCOPE_RULES` (e.g. `rules/scopes.py`) and import in both.

2. **i18n UI-method set duplicated**
   `rules/qgis_rules.py::I18N_METHODS` vs `transformers.py:127-134`
   (`I18nTransformer.i18n_methods`) — same 6 methods.
   → `from ..rules.qgis_rules import I18N_METHODS` in the transformer.

3. **Module-result shape duplicated**
   `models.ModuleAnalysis` (dataclass) vs `scanner.ModuleAnalysisResult` (TypedDict).
   → Resolved by deleting `models/`.

4. **Two security engines**
   `security_rules.py` (registry) vs `standards_visitor._check_unsafe_subprocess`.
   → Converge on one engine (§1).

`pylint R0801` found no further blocks ≥ 4 lines: structural duplication is low and
localized.

---

## 4. Optimization (complexity / size)

**Modules over the 400-line limit**: `engine.py` 540, `fixer.py` 470,
`summary_reporter.py` 424, `commands.py` 408.

**CC rank C (radon)**:
`standards_visitor.visit_For` **18**, `i18n_visitor.visit_Constant` **17**,
`engine.ProjectAnalyzer.run` **16**, `commands.handle_fix` **14**,
`scoring._get_maint_score` **13**, `html_reporter.generate_html_report` **13**,
plus 9 more at 11–12.

**Pylint design**: `scanner.analyze_module_worker` (17 locals),
`aggregators.get_research_summary` (20 locals), `html_reporter` (10 arguments),
`composite_visitor` (16 attributes), `engine` classes (8 attrs).

**Low coverage (risk areas)**: `graph.py` 28 %, `fixer.py` 28 %, `serve.py` 43 %,
`summary_reporter.py` 47 %, `cli/base.py` 56 %; `engine._filter_issues_by_scope`
(lines 479-540) fully uncovered.

Recommendations: extract private "steps" in `ProjectAnalyzer.run`; split
`fixer`/`summary_reporter` into submodules; review `scoring` ↔ `aggregators` overlap (both
aggregate project metrics).

---

## 5. Cross-tool boundary guardrails

### 5.1 With `ai-context-core` (config compiler)

Its external source (`ai_context_core/sources/external/qgis_analyzer.py`) consumes
`analysis_results/project_context.json` (**schema v1**). Contractual keys that must remain
stable:

- Top level: `schema_version`, `analyzer_version`, `project_name`, `modules`, `metrics`,
  `semantic`.
- `modules[]`: `path`, `lines`, `file_size_kb`, `complexity`, `imports`, `classes`,
  `functions`, `docstrings`, `has_main`, `syntax_error`.
- `metrics`: `total_lines`, `maintainability_score`, `quality_score`, `test_files_count`.
- `semantic`: `coupling_metrics` (`fan_in`, `fan_out`), `circular_dependencies`.

If any of these change, bump `schema_version` and coordinate. Do **not** add
structure/git/Mermaid graph generation to the analyzer — `ai-context-core` owns those
(context-only contract v5.0.0).

### 5.2 With `qgis-plugin-manager`

It delegates to the analyzer CLI (`qgis_manager/cli/analyzer.py`):
`qgis-analyzer --version`, `analyze <path>`, `security --deep [--strict] [-o OUT]`.
Do **not** rename subcommands or flags. Fixing §1 improves the Manager too. Do not add
packaging/deploy/compile to the analyzer (the Manager owns lifecycle); keep the analyzer
read-only analysis. Name overlap `analyzer.validators.validate_metadata` /
`validate_plugin_structure` vs `qgis_manager.validation.validate_metadata` /
`validate_project_structure`: treat the Manager as authoritative for packaging/metadata
validation and keep the analyzer's version informative.

---

## 6. Prioritized backlog

| Priority | Action | Impact | Risk |
| :--- | :--- | :--- | :--- |
| **P0** | Reconnect `security_rules` + regression test | Restores Bandit scanning (analyzer + manager) | Low |
| **P1** | Extract `SCOPE_RULES`; reuse `I18N_METHODS` | SSoT, removes scope drift | Low |
| **P1** | Delete `models/`, `modernization_rules`, dead helpers | −229 LOC | Low |
| **P2** | Wire/remove `calculate_package_size`, `scan_for_binaries` | Clear public API | Low |
| **P2** | Split `engine`/`fixer`/`summary_reporter`; lower CC of `run`/`visit_For`/`visit_Constant` | Maintainability | Medium |
| **P3** | Raise coverage of `graph`/`serve`/`fixer` (28–47 %) | "Zero Bug" confidence | Low |

---

*Generated as an ad-hoc deep analysis; no source or configuration was modified.*
