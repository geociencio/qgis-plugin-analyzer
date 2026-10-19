# Deep Analysis Report — qgis-plugin-analyzer v1.16.0

**Scope**: full repository audit — architecture, quality gates, packaging, documentation,
CLI behavior and feature accuracy.

**Source under analysis**: repository at `qgis_plugin_analyzer/`, branch `main`,
commit `b420a43` (one commit after tag `v1.16.0`), `version = "1.16.0"`.

**Analysis date**: 2026-10-19.

**Method / tooling** (no source changes):

| Tool | Purpose | Result |
| :--- | :--- | :--- |
| `ruff` 0.14.10 | lint + format | **clean** (`check` + `format --check`, 113 files) |
| `mypy` 1.19.1 | static typing | **clean** (72 source files) |
| `pytest` 9.0.2 + `pytest-cov` | test suite + coverage | **233 passed**, **87 %** total coverage |
| `qgis-analyzer` (self-run) | dogfooding | 10 findings, all `LOW`; strict profile green |
| `ruff --select C901` | independent CC | 2 functions above CC 10 |
| `ruff --select B,SIM,PERF` | extended lint | 36 SIM/PERF + 7 S findings (mostly explainable) |
| `forge.py validate` | agent-system consistency | 15 skills / 14 workflows pass |
| Synthetic QGIS plugins | behavioral probes | 4 confirmed behavior defects |

All probes were executed against throw-away projects under `/tmp`; no repository file was
modified except this report. Dynamic checks used the project venv (Python 3.12.12);
CI covers 3.11/3.12/3.13.

---

## 1. Executive summary

`qgis-plugin-analyzer` is a **mature, well-maintained codebase**. The core architecture is
coherent, the automated gates are green, and the engineering discipline (typed public API,
Google docstrings, unified rule catalog, deterministic incremental cache, stdlib-only
runtime) is clearly above average for a project of this size.

**The release is healthy at the library/CLI-core level, but the audit found four
user-visible behavior defects and several packaging/documentation drifts** that the
existing test suite does not catch:

1. **Qt resource validation is wired but dead** — the advertised "missing resource"
   detection never reports anything (`resource_usages` is never populated).
2. **`qgis-analyzer security` does not run the security scope** — it silently runs the
   full `all` scope (slower, noisy context) and `--deep` is a no-op flag.
3. **The composite GitHub Action pins Python 3.10**, while the package requires
   `>= 3.11` — the action cannot install the tool.
4. **`# noqa` does not suppress security findings**, contradicting the documented
   "transversal" suppression contract.

None of these is a P0 blocker for a PyPI/CLI release (the core analyzer works), but 1–2
directly invalidate features advertised in the README, and 3 breaks a distribution
channel. They should be fixed before the next minor release.

**Overall grade: B+ (good, with targeted correctness and packaging work remaining).**

---

## 2. Verification scorecard

| Gate | Command | Result |
| :--- | :--- | :--- |
| Lint | `ruff check .` | ✅ All checks passed |
| Format | `ruff format --check .` | ✅ 113 files already formatted |
| Types | `mypy src/` | ✅ Success: no issues in 72 source files |
| Tests | `pytest tests/ -q` | ✅ 233 passed in ~1.1 s |
| Coverage | `pytest --cov=analyzer` | ✅ 87 % (CI floor 80 %) |
| Self-analysis | `qgis-analyzer analyze . --max-cc 15` | ✅ exit 0; 10 LOW findings |
| Release profile | `qgis-analyzer analyze . --profile release --strict` | ✅ exit 0 |
| Rules docs | `python scripts/generate_rules_md.py --check` | ✅ RULES.md up to date |
| Agent system | `forge.py validate` / `--graph` | ✅ 15 skills, 14 workflows |
| Version consistency | `qgis-analyzer version` | ✅ 1.16.0 (pyproject + uv.lock) |

### Metrics snapshot

| Metric | Value |
| :--- | ---: |
| Source files / lines | 72 / 10,111 (analyzer reports 10,183 counted lines) |
| Test files / lines | 38 / 3,416 |
| Functions analyzed | 377 |
| Average / median CC | 3.92 / 4 (max 13) |
| Functions above CC 10 | 12 (analyzer metric) / 2 (ruff mccabe) |
| Circular dependencies | 0 |
| Max fan-in / fan-out | 10 (`cli/base.py`) / 10 (`engine.py`) |
| Module Stability | 54.6 / 100 |
| Maintainability | 99.9 / 100 |
| Security (Bandit-inspired) | 100.0 / 100 |
| Type hints (params / returns) | 100.0 % / 98.9 % |
| Docstrings | 100.0 % (Google) |
| Rule catalog | 52 entries, 51 emitted |

---

## 3. Architecture review

### 3.1 Pipeline (as implemented)

```
CLI (argparse) ──▶ commands.py ──▶ ProjectAnalyzer.run(scope)
                                        │
                    ┌───────────────────┼────────────────────┐
                    ▼                   ▼                    ▼
          discover_project_files   parallel_analysis     semantic.py
                    │                   │                    │
                    ▼                   ▼                    ▼
                scanner.py ──▶ CompositeVisitor ──▶ visitors/*
                    │                   │
                    │                   └──▶ rules.registry (catalog/scopes)
                    ├──▶ SecurityVisitor + SecretScanner   (second AST pass)
                    └──▶ audit_qgis_standards (regex)
                                        │
                                        ▼
                             aggregators.build_analysis_results
                                        │
                                        ▼
                        reporters/* (console, Markdown, HTML, JSON)
```

### 3.2 What is architecturally sound

- **Clean separation of concerns** between CLI, engine, visitors, rule metadata,
  aggregators and reporters. The `cli/commands/*` classes are thin argparse adapters.
- **Unified rule catalog** (`rules/catalog*.py` → `registry.py` → `scopes.py`) is a real
  single source of truth; `RULES.md`, `list-rules` and scope filtering all derive from it,
  with a drift test (`tests/test_rule_registry.py:179`).
- **Pure AST visitors**: no visitor performs file I/O; detection is separated from
  reporting (`BaseVisitor._report_issue`).
- **Deterministic incremental cache** (`module_cache.py`): content hash + analyzer source
  fingerprint + resolved path + effective config, with path-sorted output.
- **Zero runtime dependencies**: everything is stdlib; `dominate` is no longer used and
  the claim in the old project-context skill is stale.
- **Safety engineering**: SSRF guard before URL probing (`validators.py:24`), path
  normalization, `errors="replace"` on file reads, explicit `TypedDict` output contract.

### 3.3 Architectural deviations worth tracking

| Deviation | Evidence | Impact |
| :--- | :--- | :--- |
| `scanner.py` is a second orchestrator, not just discovery/read | it parses AST, runs `CompositeVisitor`, `SecurityVisitor`, `SecretScanner`, regex audit and Halstead metrics (`scanner.py:140-195`) | documentation (`AGENTS.md`) understates its role; 8-module fan-in makes it a coupling hotspot |
| Security is a **second full AST traversal** | `_collect_security_issues` re-visits the tree (`scanner.py:290-315`) | contradicts the "single-pass" claim; double traversal cost |
| `SecurityVisitor` bypasses `BaseVisitor` | `class SecurityVisitor(ast.NodeVisitor)` (`visitors/security_visitor.py:9`) | different severity/config/suppression semantics (see F-05) |
| Scope→visitor map duplicated | manual `if/elif` in `CompositeVisitor.__init__` (`composite_visitor.py:63-95`) vs `SCOPE_RULES` | two sources of truth for scopes (already in `next_steps.md`) |
| Complexity gate lives in the CLI layer | `_enforce_max_cc` / `_report_and_gate` (`commands.py:168-223`) | not reusable by library consumers; the gate is not part of the engine contract |

---

## 4. Findings

Severity scale: **P1** = user-visible defect / broken channel, **P2** = correctness or
security weakness, **P3** = hygiene / documentation / maintainability.

### F-01 — P1 — Qt resource validation never reports missing resources (dead feature)

**Claim**: README advertises "Qt Resource Validation: Detects missing/broken resource
paths (`:/plugins/...`)" (`README.md:34`).

**Reality**: `ModuleAnalysisResult.resource_usages` is declared (`scanner.py:75`) and
always filled with `getattr(visitor, "resource_usages", [])` (`scanner.py:184`), but **no
visitor defines that attribute** — a repository-wide search finds only the consumer side
(`semantic.py:289-292`). The semantic analyzer therefore always calls
`validate_usage([])` (`semantic.py:244-259`), which returns `[]`.

**Evidence** (synthetic QGIS plugin referencing a non-existent resource):

```
$ qgis-analyzer analyze /tmp/plugin -o /tmp/out
project_type: qgis
missing_resources: []
module resource_usages: [[]]
```

The `.qrc` scanner works, but no code path extracts `:/...` strings from Python sources.

**Impact**: a documented QGIS-specific check is a permanent false negative — every plugin
gets a clean "Missing Resources" result. Existing tests only exercise `ResourceValidator`
directly (`tests/test_semantic.py:62`), so the end-to-end gap is invisible.

**Recommendation**:
1. Add a `ResourceUsageVisitor` (or a small collector in `scanner.py`) that extracts
   `:/plugins/...` strings from `ast.Constant` values and `self.tr(...)`/path helpers.
2. Populate `results["resource_usages"]` from it, and add an end-to-end test with a
   minimal `.qrc` + a missing path.
3. Until fixed, remove the claim from `README.md` to avoid promising a non-working check.

---

### F-02 — P1 — `qgis-analyzer security` ignores the security scope; `--deep` is a no-op

**Reality**: `handle_security` calls `analyzer.run()` with the default scope (`all`),
not `scope="security"` (`commands.py:308`). The dedicated command therefore performs a
full analysis (i18n, performance, architecture, docstrings, …) and writes an unfiltered
`project_context.json`; only the terminal report is filtered by `by="security"`.

**Evidence** (security-focused run over a plugin containing `eval` and `os.system`):

```
$ qgis-analyzer security /tmp/plugin -o /tmp/out
ast: ['MISSING_DOCSTRING', 'MISSING_DOCSTRING', 'MISSING_TYPE_HINTS']
sec: [('B307', 'high')]

$ qgis-analyzer analyze security /tmp/plugin -o /tmp/out
ast: ['UNSAFE_SUBPROCESS']
sec: [('B307', 'high'), ('B602', 'high')]
```

The first output proves the "focused" command actually ran the `all` scope; the second
shows the intended filtering.

**Also**: `--deep` is documented as "more intensive (but slower) security checks"
(`README.md:269`), but it only prints a message (`commands.py:305-306`). Entropy analysis
runs unconditionally in `SecretScanner.scan_text` (`secrets.py:70-86`), so the flag has no
effect.

**Impact**: slower scans, noisy context artifact, misleading CLI contract, and a
documented flag that users will believe changes coverage.

**Recommendation**:
1. Pass `scope="security"` in `handle_security`.
2. Either wire `--deep` to a real behavior (e.g. enable `HIGH_ENTROPY` + generic secrets
   only in deep mode) or remove the flag from the parser and README.
3. Add a regression test asserting `ast_issues` contains only security rule ids when
   running the `security` command.

---

### F-03 — P1 — GitHub Action pins Python 3.10 while the package requires >= 3.11

`action.yml:27` sets `python-version: "3.10"`, but `pyproject.toml:6` declares
`requires-python = ">=3.11"` (classifiers only list 3.11–3.13).

**Impact**: `pip install ${{ github.action_path }}` on the composite action fails with
"Package requires a different Python", so the published Action is unusable. Any consumer
workflow using `uses: geociencio/qgis-plugin-analyzer@...` breaks before analysis starts.

**Recommendation**: bump the action to `"3.11"` (or `"3.12"`), add a smoke job that
installs the action in a clean runner, and consider `python-version: "3.x"` with a
`>= 3.11` check.

---

### F-04 — P1/P2 — `# noqa` does not suppress security findings

The README promises "Transversal `# noqa`: Suppress any rule inline with `# noqa`
(whole line) or `# noqa: RULE_ID` (single rule)" (`README.md:47`). Suppression is applied
inside `CompositeVisitor` to visitor issues only (`composite_visitor.py:166-171`).
Security findings are built by a separate pass and never filtered
(`scanner.py:177-184`).

**Evidence**:

```python
eval("1+1")  # noqa: B307
```

```json
"security_issues": [{"type": "B307", "line": 2, ...}]
```

**Impact**: users cannot silence false positives for `B102/B301/B307/B602/B608` or secret
rules, which is exactly where noisy heuristics (entropy, generic secrets) need an escape
hatch. This also breaks the uniform suppression model the project advertises.

**Recommendation**: apply the same `collect_noqa_directives` filter to `security_issues`
in `scanner.py` (or route security findings through `BaseVisitor`), and add a test for
`# noqa` on both an AST rule and a security rule. This overlaps with the architectural
fix suggested in §3.3.

---

### F-05 — P2 — `serve` exposes reports on all network interfaces

`ServeCommand` binds `socketserver.TCPServer(("", port), handler)` (`serve.py:76`) — the
empty host means `0.0.0.0`/all interfaces — while advertising
`http://localhost:<port>`. Reports embed source snippets, file paths and analysis
metadata.

**Impact**: on a shared network, anyone who can reach the host can read the report
directory. For a developer tool handling proprietary plugin source, localhost-only is the
safe default.

**Recommendation**: bind `("127.0.0.1", port)` by default and add an explicit
`--host` opt-in for LAN use. Also restore the previous working directory after serving
(`os.chdir` at `serve.py:73` is global and never reverted).

---

### F-06 — P2 — Package is not PEP 561 typed despite the `Typing :: Typed` classifier

`pyproject.toml` declares `Typing :: Typed`, and the codebase has 100 % parameter and
98.9 % return annotations, but there is **no `py.typed` marker** anywhere in `src/` (and
no `package-data` entry to ship one).

**Impact**: mypy/pyright treat installed `qgis-plugin-analyzer` as untyped; downstream
users do not get the inline types the project invested in, and the classifier is
inaccurate.

**Recommendation**: add `src/analyzer/py.typed`, ship it via
`[tool.setuptools.package-data] analyzer = ["py.typed"]`, and verify it in the wheel.

---

### F-07 — P2 — Wheel ships a stray top-level `__init__.py`

The built `qgis_plugin_analyzer-1.16.0-py3-none-any.whl` contains a root-level
`__init__.py` entry in addition to `analyzer/…`. It originates from `src/__init__.py`
(setuptools auto-discovery maps the source root's `__init__.py` to a top-level module).

**Impact**: pollutes `site-packages` with an `__init__.py` module that never belongs
there, can collide with other distributions, and is a code smell in the sdist/wheel
contract.

**Recommendation**: delete `src/__init__.py` (it only contains a docstring) and optionally
declare explicit setuptools discovery (`[tool.setuptools.packages.find] where = ["src"]`)
to make the layout intentional.

---

### F-08 — P2 — Release workflow points at a non-existent release-body file

`.github/workflows/release.yml:30` sets:

```yaml
body_path: docs/GITHUB_RELEASE_${{ github.ref_name }}.md
```

No such file exists: historical GitHub bodies live in `docs/releases/github/` (only up to
`v1.2.0`), and the release process now tells maintainers to write
`docs/releases/notes/vX.Y.Z.md` (`docs/releases/RELEASE_PROCESS.md`, §2.4).
`fail_on_unmatched_files` only affects `files:`, not `body_path`.

**Impact**: the `draft-release` job cannot produce the documented release body (and may
fail on a missing file), so the v1.16.0 release appears to have been published manually.
The automation and the docs disagree.

**Recommendation**: change `body_path` to
`docs/releases/notes/${{ github.ref_name }}.md`, add a pre-flight `test -f` step with a
clear error, and delete or archive the obsolete `docs/releases/github/` bodies.

---

### F-09 — P2 — `--max-cc` is not enforced in `--json` mode

`_emit_json` embeds `cc_gate` / `cc_violations` but returns normally
(`commands.py:152-166`); the non-JSON path raises `SystemExit(1)`
(`commands.py:168-195`).

**Evidence**:

```
JSON mode exit=0   # --max-cc 1 with a violating function
Text mode exit=1
```

**Impact**: a CI pipeline that consumes `--json` (the documented machine-readable
contract) will pass despite complexity violations. The gate is advisory in precisely the
mode designed for CI.

**Recommendation**: exit non-zero after emitting JSON when the gate fails (stdout is
already flushed), or document explicitly that JSON mode delegates the decision to the
consumer. Prefer the former for safety.

---

### F-10 — P2 — Broad `except Exception` in the analysis worker hides failures

`analyze_module_worker` wraps the whole per-file pipeline in
`except Exception: return None` with no logging (`scanner.py:196-199`), and
`_read_file_content` does the same (`scanner.py:228-235`).

**Impact**: any analyzer bug (attribute error, encoding edge case, unexpected AST shape)
silently drops a module from the report. The user sees a smaller `total_files`/`modules`
set with no warning, and coverage/diagnostics are impossible. This is especially risky
because the project's own philosophy is "zero false negatives" for analysis rules.

**Recommendation**: catch expected failures narrowly (`OSError`, `SyntaxError`,
`RecursionError`), log unexpected exceptions at `warning` with the file path, and surface
a `skipped_files`/`errors` counter in the output contract.

---

### F-11 — P2 — HTML report does not escape analyzed content

`html_reporter.py` interpolates issue messages, code snippets, file paths, project name,
ruff messages and URL statuses directly into HTML (e.g. lines 84, 127-130, 256-259,
321). No `html.escape` is used.

**Impact**: a target plugin containing `<script>` (or simply `&`/`<` in a message) can
break the report layout and inject active content into the generated
`PROJECT_SUMMARY.html`. The report is local, but it is rendered in a browser and may be
served to the LAN (see F-05).

**Recommendation**: escape every dynamic value (`html.escape(str(value))`) and add a
regression test with a `<script>` snippet. The Markdown reporter should also escape table
pipes at minimum.

---

### F-12 — P3 — Stale configuration and duplicated code

- `pyproject.toml:74` excludes `src/analyzer/templates`, which does not exist.
- `pyproject.toml:81` grants per-file ignores to `src/analyzer/reporters.py`, but reporters
  are now a package (`src/analyzer/reporters/`); the rule never applies.
- `.analyzerignore` still lists `.gemini/` and `reproduce_bug.py`, neither present.
- `tests` config uses `pythonpath = ["."]`, which does not make `analyzer` importable from
  `src/`; tests only work because the package is installed in the venv.
- `main()` is duplicated verbatim in `analyzer/main.py:29` and `analyzer/cli/__init__.py:8`;
  only the former is the console entry point.
- `_MAX_PACKAGE_SIZE_MB = 20` is repeated in `scoring.py:31`, `validators.py:20` and
  `html_reporter.py:13`; `_SCORE_GOOD`/`_SCORE_FAIR` are repeated in `console.py:11-12` and
  `html_reporter.py:14-15`; `SEVERITY_MAP` is repeated in `scanner.py:82` and
  `visitors/base.py:14`.

**Recommendation**: remove stale paths, centralize thresholds in a small `constants.py`
(or the rule catalog for severities), and keep a single `main()`. Low risk, improves the
"single source of truth" story.

---

### F-13 — P3 — Documented complexity standard (< 10) is not enforced (gate is 15)

`.agent/skills/coding-standards/SKILL.md:54` says "Keep cyclomatic complexity below 10",
but `forge.toml`, `pyproject.toml` and CI all use `--max-cc 15`. Independent `ruff`
mccabe finds 2 functions above 10 (`_get_maint_score` CC 11, `_resolve_import` CC 11),
and the analyzer's own metric reports 12 functions above 10 (max 13).

**Impact**: the standard and the gate disagree, so the project can drift further while
still passing.

**Recommendation**: either add `C901` with `max-complexity = 10` to the ruff config and
fix/suppress the two outliers, or raise the documented standard to 15 with a rationale.
Aligning tool, gate and skill avoids "policy theatre".

---

### F-14 — P3 — Coverage is strong overall but weak on QGIS-specific paths

Total coverage is 87 %, yet several paths that matter most to the tool's domain are below
the 80 % floor:

| Module | Coverage | Why it matters |
| :--- | ---: | :--- |
| `scope_filter.py` | 33 % | scope filtering of issues |
| `qgis_checks.py` | 43 % | QGIS compliance/structure/metadata aggregation |
| `commands.py` | 63 % | CLI gates (CC, JSON, fix, security) |
| `secrets.py` | 69 % | secret/entropy detection |
| `semantic.py` | 74 % | dependency graph + resource validation |
| `transformers.py` | 77 % | auto-fix AST rewrites |
| `fixer.py` | 77 % | file mutation safety |
| `scanner.py` | 82 % | core per-module pipeline |

**Recommendation**: add integration tests that build a minimal QGIS plugin fixture
(metadata + `.qrc` + representative source) and assert the full output contract. This
single fixture would likely raise `qgis_checks`, `semantic`, `scanner` and `scope_filter`
at once, and would have caught F-01 and F-04.

---

### F-15 — P3 — Documentation drift and broken links

- `README.md:67` still says "What's New in v1.15.2" although v1.16.0 is released and the
  release process explicitly requires updating this section.
- `CONTRIBUTING.md` is stale: it says the project uses **Black** (it uses `ruff format`,
  line 57), tells contributors to run `mypy .` (line 69) and
  `python -m unittest discover tests` (line 72), claims a "native unittest" suite (line
  95), and says logic usually lives in `scanner.py` (contradicting the visitors/rules
  architecture).
- `docs/user_guide/COMMANDS_GUIDE.md` documents only 5 of the 9 commands (missing
  `security`, `graph`, `serve`, `version`).
- Four real broken relative links were found: `docs/plans/upstreaming_qgis_analyzer.md`
  → `../../scripts/upstream/i18n_ast_rule.py`, `docs/releases/notes/RELEASE_NOTES_v0.7.0.md`
  → `../CHANGELOG.md`, and two links in `docs/releases/github/GITHUB_RELEASE_v0.9.0.md`
  and `.../v1.0.0.md`.
- The project-context skill still mentions `dominate` as a core library; the runtime is
  stdlib-only.

**Recommendation**: refresh README "What's New" for v1.16.0, rewrite the CONTRIBUTING
quality commands to match `ruff`/`mypy src/`/`pytest`, complete the command guide, and fix
or archive the historical release bodies.

---

### F-16 — P3 — Quality indicators are hard to compare ("54.6 stability" vs "99.9 maintainability")

`_get_mi_score` (`scoring.py:133-140`) averages a simplified Maintainability Index over
files and subtracts `0.23 × CC + 16.2 × ln(SLOC)`; large modules are heavily penalized.
`_get_maint_score` (`scoring.py:143-197`) works at function level and is capped at 99.9
when any issue exists. The two indicators therefore diverge by 45 points on the same
codebase (54.6 vs 99.9), and the README badge shows a yellow "Module Stability 54.6"
next to a green 99.9 without explaining the difference.

**Impact**: the headline quality signal looks contradictory to users and makes
regressions hard to interpret (a stability move from 54.6 to 55 could be noise, not a
fix). It also makes the self-analysis score look worse than the code actually is.

**Recommendation**: rename the metric to what it is ("Maintainability Index (file-level)"),
document both formulas in `RULES.md`/README, and consider reporting the MI band
(A/B/C) instead of a bare percentage. If the project wants a "stability" metric, derive it
from error/exception handling rather than file size.

---

## 5. Positive findings (preserve these)

- **Deterministic output contract**: `schema_version`, `analyzer_version`, `analyzed_at`,
  `project_path`; cache results sorted by path. Explicitly guarded by
  `next_steps.md` watch-outs.
- **Cache invalidation is genuinely robust**: analyzer source fingerprint + version +
  resolved path + effective config; corrupt/mismatched caches are ignored rather than
  trusted (`module_cache.py:117-135`).
- **Security-conscious URL probing**: `is_ssrf_safe` blocks loopback/private/link-local
  and unresolvable hosts before `urlopen`, with a 5 s timeout (`validators.py:24-108`).
- **Safe XML handling**: `ElementTree` without custom entity resolution, with an explicit
  comment about XXE (`semantic.py:221-224`).
- **Documentation depth**: DEVELOPMENT_LOG, maintenance sessions, release notes, plans and
  RULES.md are far above average; the agent framework (`forge.py`) validates its own
  consistency.
- **Zero runtime dependencies** and a compact install surface.
- **Self-analysis discipline**: the project runs its own `--max-cc` gate in CI and has
  driven self-findings from 80 to 10 (all LOW).

---

## 6. Prioritized action plan

| # | Finding | Priority | Effort | Risk |
| :--- | :--- | :---: | :---: | :---: |
| 1 | F-03 Action Python 3.11+ | P1 | XS | None |
| 2 | F-02 `security` scope + `--deep` | P1 | S | Low |
| 3 | F-01 resource usage extraction | P1 | M | Low |
| 4 | F-04 `# noqa` for security | P1 | S | Low |
| 5 | F-05 bind `serve` to 127.0.0.1 | P2 | XS | None |
| 6 | F-06 `py.typed` + package-data | P2 | XS | None |
| 7 | F-07 remove `src/__init__.py` | P2 | XS | Low (rebuild wheel) |
| 8 | F-08 release `body_path` | P2 | XS | None |
| 9 | F-09 JSON mode CC exit code | P2 | S | Low (contract change) |
| 10 | F-10 narrow exceptions + log | P2 | S | Low |
| 11 | F-11 HTML escaping | P2 | S | None |
| 12 | F-12 stale config / constants | P3 | S | None |
| 13 | F-13 complexity gate alignment | P3 | S | Low |
| 14 | F-14 QGIS integration fixture | P3 | M | None |
| 15 | F-15 docs refresh | P3 | M | None |
| 16 | F-16 score nomenclature/docs | P3 | S | None |

Suggested release sequencing:

- **v1.16.1 (patch)**: F-03, F-02, F-05, F-06, F-07, F-08, F-09, F-12.
- **v1.17.0 (minor)**: F-01, F-04, F-10, F-11, plus the QGIS integration fixture (F-14)
  and the `BaseVisitor` convergence for security.
- **Backlog**: F-13, F-15, F-16, class decomposition (already tracked in
  `.agent-state/next_steps.md`), `_active_visitors`/`SCOPE_RULES` unification.

---

## 7. Reproduction appendix

### Gates

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src/
uv run pytest -q --cov=analyzer --cov-report=term
uv run qgis-analyzer analyze . --max-cc 15
uv run qgis-analyzer analyze . --profile release --strict
uv run python scripts/generate_rules_md.py --check
uv run python .agent/tools/forge.py validate --graph
```

### Synthetic probes

Minimal QGIS project used for F-01/F-02/F-04:

```text
plugin/
├── metadata.txt      # [general] name/version/email
├── resources.qrc     # <qresource prefix="/plugins/demo"></qresource>
└── plugin.py         # eval(...), subprocess.run(..., shell=True),
                      # ":/plugins/demo/missing_icon.png"
```

Commands:

```bash
qgis-analyzer analyze /tmp/plugin -o /tmp/out
qgis-analyzer security /tmp/plugin -o /tmp/out
qgis-analyzer analyze security /tmp/plugin -o /tmp/out
qgis-analyzer analyze metadata /tmp/plugin -o /tmp/out
```

Extended lint evidence:

```bash
ruff check src --select C901 --config 'lint.mccabe.max-complexity=10'
ruff check src --select S --statistics
ruff check src --select SIM,PERF --statistics
```

---

*Report generated by repository audit on 2026-10-19 against commit `b420a43`
(`v1.16.0`). No production code was modified.*
