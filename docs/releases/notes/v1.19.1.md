# v1.19.1: SIGNAL_LEAK Scope & Lifetime Fixes 🧷

Patch release for **issue #1**. No API changes: this corrects three false-negative
and false-positive paths in the signal resolver introduced in 1.19.0.

## Fixed

- **Slot-less `disconnect()` is sender-scoped.** `self.changed.disconnect()` now
  consumes only connections whose sender is `self.changed`; it no longer matches
  every pending connection in the class. This makes the duplicate
  `source → self.changed.emit` connections report as `unmatched` again.
- **Tuple-unpacked loops are expanded.**
  `for signal, slot in ((self.raster.layerChanged, self.band.setLayer),):` produces
  per-element events, so the matching `disconnect(slot)` resolves correctly.
- **Lifetime propagation.** A `deleteLater()` on a local container propagates
  `local_widget` to its child connections, and explicit custom parents such as
  `SidePanel(self)` are classified as `parent_child`. A `self.*` attribute with no
  evidence remains `unmatched`.

## Verification

The minimal reproduction in issue #1 now reports:

```text
connect_sites: 6, matched: 1, unmatched: 2, benign: 3

self.a.toggled            unmatched
self.b.toggled            unmatched
self.raster.layerChanged  matched
self.button.clicked       benign / local_widget
self.check.toggled        benign / local_widget
self.panel.changed        benign / parent_child
```

## Upgrade

```bash
pip install --upgrade qgis-plugin-analyzer
```

## Quality

- **309 tests**, 89.5% coverage; `ruff check` + `mypy src/` clean.
- Self-analysis `--max-cc 15` green with 10 LOW findings.
- Rule catalog: **56** rules; Module Stability 53.5 · Maintainability 99.9 ·
  Security 100.0.
