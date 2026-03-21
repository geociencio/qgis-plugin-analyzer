# QGIS Plugin Analyzer - CLI Commands Roadmap

This document defines the implementation strategy for new commands and subcommands for `qgis-analyzer`, organized into phases based on value/effort.

---

## 📊 Prioritization Matrix

| Command/Subcommand | Value | Effort | Phase | Priority |
|-------------------|-------|----------|------|-----------|
| `analyze` subcommands | ✅ High | ✅ Low | **Completed** | - |
| `fix` subcommands | 🔥 High | 🟢 Low | 1 | P0 |
| `docs validate` | 🔥 High | 🟢 Low | 1 | P0 |
| `search deprecated` | 🔥 High | 🟢 Medium | 1 | P1 |
| `analyze compatibility` | 🔥 High | 🟡 Medium | 2 | P1 |
| `migrate pyqt5-to-pyqt6` | 🔥 High | 🟡 Medium | 2 | P0 |
| `test generate` | 🟠 Medium | 🟡 Medium | 2 | P2 |
| `package build/validate` | 🟠 Medium | 🟡 Medium | 2 | P2 |
| `benchmark profile` | 🟠 Medium | 🔴 High | 3 | P3 |
| `docs generate` | 🟠 Medium | 🔴 High | 3 | P3 |
| `init plugin` | 🟡 Low | 🔴 High | 3 | P4 |
| Advanced `report` | 🟡 Low | 🔴 High | 3 | P4 |

---

## 🎯 Phase 1: High Impact Commands (v1.9.0)

**Objective**: Improve the daily development experience with correction and validation commands.

**Estimated Duration**: 2-3 weeks

### 1.1 `fix` with Subcommands

**Priority**: P0 | **Effort**: 3-5 days

```bash
qgis-analyzer fix i18n [path]           # Auto-wrap strings in tr()
qgis-analyzer fix imports [path]        # Corrects imports (GDAL, PyQt)
qgis-analyzer fix formatting [path]     # Applies black/isort
qgis-analyzer fix types [path]          # Adds basic type hints
qgis-analyzer fix all [path]            # Applies all corrections
qgis-analyzer fix --interactive [path]  # Interactive mode with confirmation
qgis-analyzer fix --dry-run [path]      # Preview without changes
```

**Implementation**:
- [ ] Create `FixCommand` with subparsers
- [ ] Implement `I18nFixer` (automatic wrapping)
- [ ] Implement `ImportsFixer` (import rewriting)
- [ ] Implement `FormattingFixer` (black/isort integration)
- [ ] Implement `TypeHintsFixer` (basic inference)
- [ ] Interactive mode with `rich.prompt`
- [ ] Regression tests for each fixer

**Affected Files**:
- `src/analyzer/cli/commands/fix.py` (new)
- `src/analyzer/fixers/` (new package)
  - `base_fixer.py`
  - `i18n_fixer.py`
  - `imports_fixer.py`
  - `formatting_fixer.py`
  - `types_fixer.py`

---

### 1.2 `docs validate`

**Priority**: P0 | **Effort**: 2-3 days

```bash
qgis-analyzer docs validate [path]              # Validates docstrings
qgis-analyzer docs validate --style=google      # Enforces Google style
qgis-analyzer docs validate --strict            # Strict mode
qgis-analyzer docs validate --fix               # Auto-corrects format
```

**Implementation**:
- [ ] Create `DocsCommand` with `validate` subcommand
- [ ] Docstring parser (Google/NumPy/Sphinx)
- [ ] Structure validator (Args, Returns, Raises)
- [ ] Format auto-correction
- [ ] Integration with existing `MetricsVisitor`

**Affected Files**:
- `src/analyzer/cli/commands/docs.py` (new)
- `src/analyzer/validators/docstring_validator.py` (new)
- `MetricsVisitor` extension

---

### 1.3 `search deprecated`

**Priority**: P1 | **Effort**: 3-4 days

```bash
qgis-analyzer search deprecated [path]          # Deprecated QGIS APIs
qgis-analyzer search api "QgsVectorLayer" [path] # Specific API usage
qgis-analyzer search pattern "*.connect(*)"     # Code patterns
qgis-analyzer search todos [path]               # TODOs/FIXMEs/NOTEs
```

**Implementation**:
- [ ] Create `SearchCommand`
- [ ] QGIS deprecated API database
- [ ] AST search engine for patterns
- [ ] Special comment extractor
- [ ] Formatted output with context

**Affected Files**:
- `src/analyzer/cli/commands/search.py` (new)
- `src/analyzer/search/` (new package)
  - `deprecated_apis.py`
  - `pattern_matcher.py`
  - `comment_extractor.py`
- `data/deprecated_apis.json` (new)

---

## 🚀 Phase 2: Migration and Compatibility (v2.0.0)

**Objective**: Facilitate migrations between QGIS/PyQt versions and improve testing.

**Estimated Duration**: 4-6 weeks

### 2.1 `migrate pyqt5-to-pyqt6`

**Priority**: P0 | **Effort**: 1-2 weeks

```bash
qgis-analyzer migrate pyqt5-to-pyqt6 [path]     # PyQt5 → PyQt6 migration
qgis-analyzer migrate qgis3-to-qgis4 [path]     # QGIS 4.x preparation
qgis-analyzer migrate python38-to-39 [path]     # Python update
qgis-analyzer migrate --dry-run [path]          # Preview
qgis-analyzer migrate --report [path]           # Change report
```

**Implementation**:
- [ ] AST transformation engine (`libcst` or `rope`)
- [ ] PyQt5→PyQt6 migration rules
- [ ] QGIS 3→4 migration rules
- [ ] Breaking change detection
- [ ] Migration report generation
- [ ] Interactive mode for decisions

**Affected Files**:
- `src/analyzer/cli/commands/migrate.py` (new)
- `src/analyzer/migrations/` (new package)
  - `base_migration.py`
  - `pyqt_migration.py`
  - `qgis_migration.py`
  - `python_migration.py`
- `data/migration_rules/` (new JSONs)

---

### 2.2 `analyze compatibility`

**Priority**: P1 | **Effort**: 1 week

```bash
qgis-analyzer analyze compatibility [path]      # General compatibility
qgis-analyzer analyze compatibility --qgis=3.28 # Specific version
qgis-analyzer analyze compatibility --python=3.9
```

**Implementation**:
- [ ] Extend `analyze` with `compatibility` subcommand
- [ ] QGIS/PyQt/Python compatibility matrix
- [ ] Version-specific API detection
- [ ] Dependency validation
- [ ] Incompatibility report

**Affected Files**:
- `src/analyzer/cli/commands/analyze.py` (extension)
- `src/analyzer/compatibility/` (new package)
  - `version_checker.py`
  - `api_compatibility.py`
- `data/compatibility_matrix.json` (new)

---

### 2.3 `test generate`

**Priority**: P2 | **Effort**: 1-2 weeks

```bash
qgis-analyzer test generate [path]              # Generates unit tests
qgis-analyzer test run [path]                   # Runs tests
qgis-analyzer test coverage [path]              # Coverage report
qgis-analyzer test integration [path]           # Integration tests
```

**Implementation**:
- [ ] AST-based test generator
- [ ] QGIS test templates
- [ ] pytest integration
- [ ] Test runner in QGIS environment
- [ ] Coverage reporting

**Affected Files**:
- `src/analyzer/cli/commands/test.py` (new)
- `src/analyzer/testing/` (new package)
  - `test_generator.py`
  - `test_runner.py`
  - `coverage_reporter.py`
- `templates/test_templates/` (new)

---

### 2.4 `package build/validate`

**Priority**: P2 | **Effort**: 1 week

```bash
qgis-analyzer package build [path]              # Builds .zip
qgis-analyzer package validate [zip]            # Validates package
qgis-analyzer package metadata [path]           # Generates metadata.txt
qgis-analyzer package publish [zip]             # Publishes to repository
```

**Implementation**:
- [ ] QGIS package builder
- [ ] Structure validator
- [ ] metadata.txt generator
- [ ] Client for QGIS repositories
- [ ] Digital signature validation

**Affected Files**:
- `src/analyzer/cli/commands/package.py` (new)
- `src/analyzer/packaging/` (new package)
  - `builder.py`
  - `validator.py`
  - `metadata_generator.py`
  - `publisher.py`

---

## 🔬 Phase 3: Advanced Analysis (v2.5.0)

**Objective**: Advanced profiling, documentation, and scaffolding tools.

**Estimated Duration**: 6-8 weeks

### 3.1 `benchmark profile`

**Priority**: P3 | **Effort**: 2-3 weeks

```bash
qgis-analyzer benchmark profile [path]          # Function profiling
qgis-analyzer benchmark memory [path]           # Memory analysis
qgis-analyzer benchmark startup [path]          # Startup time
qgis-analyzer benchmark compare [v1] [v2]       # Comparison
```

**Implementation**:
- [ ] `cProfile`/`line_profiler` integration
- [ ] Memory analysis with `memory_profiler`
- [ ] Startup benchmarking
- [ ] Version comparison
- [ ] Result visualization

**Affected Files**:
- `src/analyzer/cli/commands/benchmark.py` (new)
- `src/analyzer/benchmarking/` (new package)
  - `profiler.py`
  - `memory_analyzer.py`
  - `comparator.py`

---

### 3.2 `docs generate`

**Priority**: P3 | **Effort**: 2-3 weeks

```bash
qgis-analyzer docs generate [path]              # Generates documentation
qgis-analyzer docs export --format=html         # Exports to HTML/PDF
qgis-analyzer docs i18n [path]                  # Extracts strings
qgis-analyzer docs serve [path]                 # Local server
```

**Implementation**:
- [ ] API documentation generator
- [ ] Sphinx/MkDocs integration
- [ ] Translatable string extractor
- [ ] Local documentation server
- [ ] Multi-format export

**Affected Files**:
- `src/analyzer/cli/commands/docs.py` (extension)
- `src/analyzer/documentation/` (new package)
  - `generator.py`
  - `exporter.py`
  - `i18n_extractor.py`
  - `server.py`

---

### 3.3 `init plugin`

**Priority**: P4 | **Effort**: 2 weeks

```bash
qgis-analyzer init plugin [name]                # Full scaffold
qgis-analyzer init processing [name]            # Processing algorithm
qgis-analyzer init tests [path]                 # Test structure
qgis-analyzer init ci [path]                    # CI/CD configuration
qgis-analyzer init --template=modern            # Templates
```

**Implementation**:
- [ ] Template system (Jinja2)
- [ ] Full plugin scaffolding
- [ ] Processing algorithm generator
- [ ] CI/CD generator (GitHub Actions)
- [ ] Modern and legacy templates

**Affected Files**:
- `src/analyzer/cli/commands/init.py` (extension)
- `src/analyzer/scaffolding/` (new package)
  - `template_engine.py`
  - `plugin_generator.py`
  - `ci_generator.py`
- `templates/plugin_templates/` (new)

---

### 3.4 Advanced `report`

**Priority**: P4 | **Effort**: 1-2 weeks

```bash
qgis-analyzer report quality [path]             # Quality report
qgis-analyzer report security [path]            # Security report
qgis-analyzer report compliance [path]          # QGIS compliance
qgis-analyzer report --format=pdf               # Export to PDF
qgis-analyzer report --dashboard                # Interactive dashboard
```

**Implementation**:
- [ ] Advanced report generator
- [ ] PDF export (WeasyPrint)
- [ ] Interactive dashboard (Streamlit/Dash)
- [ ] Charts and visualizations
- [ ] Comparative reports

**Affected Files**:
- `src/analyzer/cli/commands/report.py` (new)
- `src/analyzer/reporting/` (extension)
  - `advanced_reporter.py`
  - `pdf_exporter.py`
  - `dashboard.py`

---

## 🌟 Transversal Features

These improvements will be applied to **all** commands incrementally:

### Phase 1 (v1.9.0)
- [ ] `--json` output for all commands
- [ ] `--config` file support (TOML/YAML)
- [ ] Improved logging with `rich`
- [ ] Consistent progress bars

### Phase 2 (v2.0.0)
- [ ] `--watch` mode (continuous analysis)
- [ ] `--cache` (incremental results)
- [ ] `--parallel` (worker control)
- [ ] Advanced `--exclude`/`--include` patterns

### Phase 3 (v2.5.0)
- [ ] Plugin system for extensions
- [ ] Public API for integrations
- [ ] Optional telemetry (opt-in)
- [ ] Auto-update

---

## 📋 New Dependencies

### Phase 1
- `black` - Code formatting
- `isort` - Import sorting
- `rich` - Improved terminal UI

### Phase 2
- `libcst` or `rope` - AST transformations
- `pytest` - Testing framework
- `coverage` - Test coverage

### Phase 3
- `cProfile`, `line_profiler` - Profiling
- `memory_profiler` - Memory analysis
- `sphinx` or `mkdocs` - Docs generation
- `jinja2` - Templates
- `weasyprint` - PDF export
- `streamlit` - Interactive dashboard

---

## 🎯 Success Metrics

### Phase 1
- [ ] 80% of `MISSING_I18N` issues auto-correctable
- [ ] 90% of incorrect imports detected and corrected
- [ ] Docstring validation time < 5s for medium projects

### Phase 2
- [ ] 95% of successful PyQt5→PyQt6 migrations without intervention
- [ ] Generated test coverage > 60%
- [ ] Packages validated 100% compatible with QGIS repository

### Phase 3
- [ ] Bottleneck identification in < 1 minute
- [ ] Generated documentation ready for publication
- [ ] Scaffolded plugins working without modifications

---

## 📅 Estimated Timeline

```mermaid
gantt
    title QGIS Analyzer - Commands Roadmap
    dateFormat  YYYY-MM-DD
    section Phase 1
    fix subcommands           :2026-02-15, 5d
    docs validate             :2026-02-20, 3d
    search deprecated         :2026-02-23, 4d
    
    section Phase 2
    migrate pyqt5-to-pyqt6    :2026-03-01, 14d
    analyze compatibility     :2026-03-15, 7d
    test generate             :2026-03-22, 14d
    package build/validate    :2026-04-05, 7d
    
    section Phase 3
    benchmark profile         :2026-04-15, 21d
    docs generate             :2026-05-06, 21d
    init plugin               :2026-05-27, 14d
    advanced report           :2026-06-10, 14d
```

---

## 🔄 Implementation Process

For each command/subcommand:

1. **Design** (1-2 days)
   - CLI specification
   - Architecture design
   - Test definition

2. **Implementation** (according to effort)
   - Base code
   - Unit tests
   - Inline documentation

3. **Testing** (1-2 days)
   - Integration tests
   - Manual testing
   - Validation with real plugins

4. **Documentation** (1 day)
   - Updated README
   - Usage examples
   - CHANGELOG

5. **Release** (1 day)
   - Version tag
   - PyPI publication
   - Community announcement

---

## 📝 Implementation Notes

- All commands must follow the pattern established in `BaseCommand`
- Maintain backward compatibility in each release
- Document breaking changes clearly
- Include regression tests for each feature
- Use type hints in all new code
- Follow Google docstring style

---

**Last updated**: 2026-02-14
**Current version**: 1.8.0-beta.1
**Next release**: 1.9.0 (Phase 1)
