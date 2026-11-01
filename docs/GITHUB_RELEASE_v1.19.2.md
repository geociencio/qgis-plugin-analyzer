# v1.19.2: SIGNAL_LEAK Parent & Loop Corrections 🧩

Patch release for the follow-up findings in **issue #1**. Fixes the false
`parent_child` classification, the remaining tuple-loop pairing bug, and literal
`list`/`tuple` loop recovery.

## Fixed

- **R4 — translated text is not a parent.** Constructor calls such as
  `QRadioButton(self.tr("A"))` are no longer treated as parented widgets. Only an
  explicit `self`/`parent` expression in the first argument produces a
  `parent_child` hint, so the three `Tab` connections remain `unmatched`.
- **R6 — sender/slot pairing.** Tuple-unpacked loops now pair each expanded
  sender with its own slot. A three-pair `for signal, slot in (...)` loop resolves
  all three disconnects instead of reusing the first slot.
- **R5 — list/tuple wrappers.** `list([...])` and `tuple([...])` iterables are
  unwrapped, so `for task in list([self.task]): task.finished.disconnect()`
  resolves the original connection.
- **R3 — parent hints.** `addWidget`/`addTab`/`setWidget` now provide a
  same-module parent-child hint for child panels. Cross-module ownership (for
  example a panel created in `main_window.py` and wired in `main_dialog.py`) is
  still reported as `unmatched`/`low` rather than guessed as benign.

## Verification

The 7-site reproduction from the issue now reports:

```text
connect_sites: 7, matched: 4, unmatched: 3, benign: 0

Tab   self.a.toggled           unmatched
Tab   self.b.toggled           unmatched
Tab   self.reset.clicked       unmatched
Dem   self.raster.layerChanged -> self.band.setLayer    matched
Dem   self.raster.layerChanged -> self.update_stats     matched
Dem   self.band.bandChanged    -> self.update_stats     matched
Tasks self.task.finished       -> self.on_finished      matched
```

This matches the expected output for R4/R5/R6: `Tab` 3 `unmatched`, `Dem` 0
`unmatched`, `Tasks` 0 `unmatched`.

## Upgrade

```bash
pip install --upgrade qgis-plugin-analyzer
```

## Quality

- **313 tests**, 89.5% coverage; `ruff check` + `mypy src/` clean.
- Self-analysis `--max-cc 15` green with 10 LOW findings.
- Rule catalog: **56** rules; Module Stability 53.5 · Maintainability 99.9 ·
  Security 100.0.
