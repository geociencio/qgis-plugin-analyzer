# v1.19.0: Signal Connection Resolution 🔗

Minor release. `SIGNAL_LEAK` is no longer a file-local literal string diff: the
analyzer now collects per-connection events, resolves aliases and loop variables,
matches slots within a configurable scope, and reports every connection with
location and confidence.

## Added

- **Per-connection signal analysis**: `research_metrics.qgis_context.signal_connections`
  now exposes `file`, `line`, `scope`, `sender`, `receiver`, `slot`, `status`,
  `confidence`, `lifetime` and `connection_type` for every connect site.
  `qgis_context_summary.signal_connections` aggregates the project.
- **Alias and loop resolution**: `widget = self.dialog.preview` and
  `for signal in (self.a.toggled, self.b.toggled)` are expanded into per-connection
  events instead of one literal string.
- **Slot and duplicate handling**: `disconnect()` consumes all matching slots,
  `disconnect(slot)` consumes one, duplicate connections remain visible and
  `Qt.UniqueConnection` is deduplicated.
- **Conservative lifetime classification**: `deleteLater`, explicit `QWidget(parent)`
  / `setParent` and bounded `destroyed` hooks become `benign`; a `self.*` attribute
  without evidence stays unmatched.
- **`analyze --signals`** prints the detailed informational list; the default summary
  shows only a one-line count.
- **`SIGNAL_LEAK` profile config**:
  ```toml
  [tool.qgis-analyzer.profiles.default.rules.SIGNAL_LEAK]
  emit = false
  scope = "class"           # function | class | file
  confidence = "low"
  include_benign = false
  ignore_senders = []
  ignore_paths = []
  ```
- **Cross-module awareness**: a connect in one module with a disconnect in another is
  reported as `unmatched` with `confidence="low"`; it is never silently resolved.

## Changed

- `SIGNAL_LEAK` is still informational by default. Use `emit=true` to append normal
  issues before scoring and make it gate-capable.
- The summary banner changed from `🚨 Signal Leaks Detected` to
  `ℹ️ Unmatched signal paths: N (informational)`.
- Signal collection is cached per module; scope/confidence/lifetime changes are
  resolved at project level without re-analyzing unchanged files.
- `signal_leaks` remains as a deprecated sorted sender-string list. Use
  `signal_connections.items` as the source of truth.

## Notes

- `include_benign=false` keeps benign records in JSON and in the `benign` summary
  count, but excludes them from the default leak list. `--signals` with
  `include_benign=true` also prints benign details.
- Dynamic composition (`getattr`, dict/list indexing, `QObject.disconnect` static
  forms, runtime `sender()`) stays low confidence/unsupported.
- No analyzer behavior changed for CC, i18n, security or module-size gates.

## Upgrade

```bash
pip install --upgrade qgis-plugin-analyzer
```

```bash
qgis-analyzer analyze . --signals
qgis-analyzer analyze . --signals --exclude '!tests/'
```

## Quality

- **305 tests**, 89.54% coverage; `ruff check` + `mypy src/` clean.
- Self-analysis `--max-cc 15` green with 10 LOW findings.
- Rule catalog: **56** rules; Module Stability 53.6 · Maintainability 99.9 ·
  Security 100.0.
