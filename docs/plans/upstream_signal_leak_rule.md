# Upstream Fix Plan: `qgis-plugin-analyzer` SIGNAL_LEAK Heuristic

> **Audience**: `qgis-plugin-analyzer` maintainer or an AI coding agent working on
> that repository.
> **Baseline analysed**: `qgis-plugin-analyzer` **1.18.1** (2026-11-01).
> **Status**: ✅ **IMPLEMENTED (unreleased)** — core collector/resolver landed;
> see implementation notes below.
> **Companion**: SecInterp's implementation plan
> [implementation_plan_v3.12.1_signal_idempotency.md](implementation_plan_v3.12.1_signal_idempotency.md).
> **Why this matters**: on the SecInterp corpus the rule reports 47 "signal leaks";
> none is a dangling connection, while the real duplicate-connection bug is only
> partially visible (3 of 16 connection sites).
>
> **Implementation notes (2026-11-01)**: landed in `signal_analysis.py`
> (cacheable event collector with aliases, loop expansion and lifetime hints) and
> `signal_resolver.py` (project-level scope/slot matching, duplicate and
> `UniqueConnection` handling, cross-module low confidence). The engine resolves
> before scoring, writes `signal_connections` to per-module and summary JSON,
> keeps the deprecated `signal_leaks`, and only emits `SIGNAL_LEAK` issues with
> `emit=true`. `analyze --signals` prints the detailed informational list. Tests:
> 305 passing. Deviation: `include_benign` controls benign detail in the human
> list; benign records remain in JSON and in the benign count.

---

## 1. Executive summary

`SIGNAL_LEAK` is currently a **file-local literal string diff**:

- It collects every `.connect(...)` and `.disconnect(...)` attribute chain in a
  module and reports `connections - disconnections`.
- It is `emitted=False` (informational), so it never enters the issue list or a
  gate, but the summary reporter prints it as `🚨 Signal Leaks Detected`.
- It has no receiver identity, slot identity, scope, line number or lifetime
  awareness.

That produces both directions of error:

- **False positives**: a real disconnect written through a loop variable or an
  alias is invisible to the matcher.
- **False negatives**: a connection written through a loop variable is invisible,
  and a signal with two slots is considered "handled" as soon as one slot is
  disconnected.

The revised proposal fixes the contract first, then the resolver:

1. **PR 1 — honest contract:** rename the concept to "unmatched connect/disconnect
   paths", stop printing the 🚨 banner, document the heuristic truthfully, and keep
   the legacy `signal_leaks` key.
2. **PR 2 — collector + resolver:** collect per-connection events, resolve simple
   aliases and loop variables, match per `(scope, sender, receiver, slot)`, count
   duplicate connections, and expose stable JSON.
3. **PR 3 — lifetime:** classify `deleteLater()`, explicit parent/child wiring and
   `destroyed.connect()` conservatively; never mark a connection benign without
   evidence.
4. **PR 4 — optional cross-module:** report connections that are disconnected in
   another module as **low confidence**, never silently resolved.

The key architectural correction is to **separate collection from resolution**:
collection is cacheable and configuration-independent; resolution is project-wide
and must run before scoring if `emit=true` is ever used for a gate.

## 2. Current implementation (verified on 1.18.1)

| Element | Location | Behaviour |
| :--- | :--- | :--- |
| State | `SafetyVisitor` (`connections`, `disconnections`) | Two `set[str]` attributes; unique sender strings only. |
| Collection | `SafetyVisitor.visit_Call` | `func_name.endswith(".connect")` / `.disconnect`; stores the attribute chain before the method. |
| Chain builder | `SafetyVisitor._get_full_attribute_name` | Handles only `ast.Name` and `ast.Attribute`; a `Call`/`Subscript` in the chain returns `""`, truncating call chains. |
| Result | `SafetyVisitor.signal_leaks` | `sorted(connections - disconnections)`; no file, line, slot or scope. |
| Docstring | `SafetyVisitor` class docstring | Claims "connected in `initGui`, not disconnected in `unload`" — not what the code does. |
| Rule catalog | `SIGNAL_LEAK` in `catalog_core.py` | Severity `low`, `emitted=False`, scope-less, informational. |
| Aggregation | `aggregators.get_research_summary` | `set.update(...)` across modules; unique strings only. |
| Summary | `summary_reporter` | Prints `🚨 Signal Leaks Detected: N` and every string unconditionally. |
| Tests | `tests/test_safety.py` | Only a literal direct match; no loops, aliases, slots, lifetime or scopes. |

Observed consequences:

- 49 per-module entries → 47 unique because sender strings repeat across files.
- 67 `.connect()` sites collapse into those 47 strings; several strings represent
  4–5 connections.
- A call chain such as `self.iface.mapCanvas().xyCoordinates.connect(...)` is
  truncated to `.xyCoordinates`, so unrelated call chains can collide.

## 3. Defects

### D1 — Literal matching only (false positives)

```python
for signal in (self.a.toggled, self.b.toggled):
    signal.disconnect()
# connects: self.a.toggled, self.b.toggled
# disconnects: signal
# => both reported as leaks
```

SecInterp: 29 of the 47 entries follow this pattern.

### D2 — No lifecycle scope (semantic mismatch)

The docstring claims `initGui()` → `unload()`, but matching is file-wide. A connect
in `__init__` and an unrelated literal `.disconnect()` anywhere in the file count
as matched, even if the disconnect never runs.

### D3 — Unique sender strings collapse connections (false negatives)

Five connections to the same signal are one set entry. Two connections to the same
signal are one entry. The rule cannot say "4 of 5 connections are unresolved".

### D4 — Global aggregation hides per-file context

The cross-module `set` loses file and line. Two files using the same sender string
become one entry and the summary count is unstable as files move.

### D5 — No slot identity (false negatives)

Qt distinguishes `sender.signal.disconnect()` (all slots) from
`sender.signal.disconnect(slot)` (one slot). The current sets do not model slots.
Once one slot is disconnected, the whole sender looks resolved, hiding a second
connected slot.

### D6 — No Qt lifetime awareness (false positives)

Child widgets destroyed with their parent, or via `deleteLater()`, are reported as
leaks even though Qt removes their connections when the object is destroyed.

### D7 — Loop-connected signals are invisible (false negatives)

```python
for signal in (self.a.toggled, self.b.toggled):
    signal.connect(self.changed.emit)
# connect path is "signal" → not collected
```

SecInterp: 13 connections in `symbology_tab.py:326-343` are invisible, including
the real duplication bug.

### D8 — Misleading presentation

The rule says "leak" and prints a 🚨 alert, but:

- `emitted=False` means it cannot fail a gate;
- the output has no `file:line`, slot, confidence or lifetime;
- there is no way to opt out of the banner or mark known-benign patterns.

### D9 — Call-chain truncation (false collisions)

`_get_full_attribute_name` returns `""` for `ast.Call`/`ast.Subscript`, so
`self.iface.mapCanvas().xyCoordinates.connect(...)` becomes `.xyCoordinates`.
Different call chains with the same tail can be matched incorrectly.

### D10 — No connection type (`Qt.UniqueConnection`)

`connect(slot, Qt.UniqueConnection)` prevents duplicate connections, but the
current model counts strings and ignores the connection type. It also cannot
distinguish `QueuedConnection`/`DirectConnection`, although those do not affect
leak detection.

### D11 — No receiver identity

`connect(self.on_a)` and `connect(self.on_b)` to the same sender are different
connections. The current model has no receiver field and cannot match slots
correctly when only one is disconnected.

## 4. Design goals

1. **No false green.** A signal with two slots and one disconnect must report the
   other slot.
2. **No false alarm.** A correct disconnect through a loop variable or alias must
   be resolved.
3. **Location and confidence.** Every entry carries `file`, `line`, `scope`,
   `sender`, `receiver`, `slot`, `status`, `confidence`, `lifetime`.
4. **Count connections, not strings.** Duplicate connections are visible; the
   summary counts connection sites.
5. **Lifetime is not a leak.** `deleteLater` / explicit parent-child /
   `destroyed` cleanup are benign only when there is evidence.
6. **Cache-friendly.** Raw collection is independent of reporting config; the
   resolver is a project-level pass.
7. **Backward compatible.** `qgis_context.signal_leaks` keeps working until the
   next major version.
8. **No new gate by default.** The rule remains informational unless a project
   opts in with `emit=true`.
9. **JSON is always additive.** Structured signal data is always present; only
   the human banner is opt-in.

## 5. Architecture

### 5.1 Pipeline placement

```text
per-module workers
  └─ SignalCollector: raw SignalEvent[] (cacheable, config-independent)
       ↓
engine, after parallel analysis / before scoring
  └─ SignalResolver: scope matching, slots, lifetime, confidence, cross-module
       ├─ SignalReport (summary + items)
       └─ if emit=true: append SIGNAL_LEAK issues before scoring
       ↓
aggregators / reporters
  └─ research_metrics.qgis_context.signal_connections
  └─ qgis_context_summary.signal_connections
  └─ legacy signal_leaks
```

- The collector must not depend on `include_benign`, `scope`, `confidence` or
  `emit`; otherwise the module cache would return stale results.
- The resolver runs once per project and can see all modules; this is the only
  place where cross-module matching can work.
- `emit=true` must append issues **before** `ScoringEngine.calculate_project_scores`
  and before `build_analysis_results`; otherwise a gate would see a score that
  ignored the issue.

### 5.2 Scope definitions

| Scope | Definition | Typical use |
| :--- | :--- | :--- |
| `function` | Connect and disconnect in the same `FunctionDef`. | Strict local check. |
| `class` | All methods of the same class (including `__init__`, `initGui`, `unload`). | **Default.** |
| `file` | Anywhere in the module. | Legacy-like checks; noisy. |
| cross-module | Different modules. | Low confidence, never resolved by default. |

This resolves an inconsistency in the first draft: with `scope="class"`, a
connection in `__init__` **is** matched to a disconnect in `unload`; `scope="file"`
is only needed across functions of different classes.

### 5.3 Data model

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class SignalEvent:
    file: str
    line: int
    scope: str                  # "Class.method" / "function"
    class_name: str | None
    function_name: str
    kind: str                   # "connect" | "disconnect"
    sender: str                 # canonical chain, including call expressions
    receiver: str | None        # canonical receiver expression, if known
    slot: str | None            # canonical slot/callback, if known
    connection_type: str        # auto | unique | queued | direct | unknown
    lifetime: str | None        # local_widget | parent_child | destroyed_hook
    confidence: str             # high | medium | low
    text: str                   # source excerpt, only for unmatched/verbose
    order: int                  # stable tie-breaker
```

Resolved output:

```python
@dataclass(frozen=True)
class SignalRecord:
    event: SignalEvent
    status: str                 # matched | unmatched | benign
    reason: str
```

`sender` includes the signal path (`self.btn.clicked`); `receiver` and `slot` are
canonical expressions. `connection_type` is **not** a lifetime.

### 5.4 Collection

Per function/class scope, build a small symbol table:

1. **Alias assignments**
   ```python
   widget = self.dialog.preview_widget
   symbology = self.dialog.page_settings.symbology_tab
   ```
   Resolve `widget`, `symbology` and transitive aliases (depth cap 8). Do not
   resolve a name that is reassigned to different expressions; mark low confidence.
2. **Signal loops**
   ```python
   for signal in (self.a.toggled, self.b.toggled):
       signal.connect(...)
   ```
   Expand the loop target to each literal tuple/list item for the loop body.
   Emit one event per item, not one `signal` string.
3. **Literal signal aliases**
   ```python
   changed = self.changed
   changed.connect(...)
   ```
   Resolve to `self.changed`; transitive with the same cap.
4. **Canonical sender**
   Preserve `Call` expressions:
   `self.iface.mapCanvas().xyCoordinates` must not become `.xyCoordinates`.
   Use `ast.unparse(node.func.value)` (or an equivalent canonicalizer) for the
   sender and slot.
5. **Do not attempt**
   dict/list indexing, `getattr(obj, name)`, runtime composition, cross-module
   imports. Keep the literal text and mark `confidence="low"`; do not drop the
   event.

### 5.5 Matching

Match within the configured scope, default `class`:

```text
for each connect event C, in source order:
    candidates = pending disconnect events D in the same scope where
        D.sender == C.sender and
        (D.receiver is None or D.receiver == C.receiver) and
        (D.slot is None or D.slot == C.slot)
    if D.slot is None:
        consume all pending C with the same sender/receiver
    else:
        consume one C, deterministically by (line, order)
    if a candidate exists:
        C.status = "matched"
    else:
        C.status = "unmatched"
```

Semantics to model explicitly:

| Form | Meaning |
| :--- | :--- |
| `sender.signal.disconnect()` | Remove all slots for that signal. Consume all pending connects for that sender. |
| `sender.signal.disconnect(slot)` | Remove one `(sender, slot)` connection. Consume one; duplicates remain unmatched. |
| `sender.disconnect()` / `QObject.disconnect(...)` | Object-level/static form; semantics differ. Mark `confidence="low"` and do not resolve unless explicitly supported. |
| `connect(..., Qt.UniqueConnection)` | Deduplicate the connect before matching; never report a duplicate. |
| `connect(..., Qt.QueuedConnection/DirectConnection)` | Keep `connection_type`; it does not affect leak matching. |

The resolver must process events deterministically (file, line, order) so duplicate
connections produce stable results. A disconnect with a slot only resolves one
connection, not the whole sender.

### 5.6 Lifetime classification

Run a separate pass over the events. **Only evidence-backed cases become benign.**

| Evidence | Classification | Confidence |
| :--- | :--- | :--- |
| Sender/receiver is a local widget with `.deleteLater()` | `local_widget` | medium |
| Explicit `QWidget(parent)` or `setParent(...)` wiring | `parent_child` | medium/high |
| `sender.destroyed.connect(cleanup)` and sender lifetime is bounded | `destroyed_hook` | medium |
| `Qt.UniqueConnection` | **not lifetime**; dedupe only | — |
| Sender is `self.*` but no parent/deleteLater/destroyed evidence | `None`; remains unmatched | low |

Do **not** classify a connection as `parent_child` merely because the sender is
stored in `self.*` and the receiver is `self`. That is not proof of Qt ownership
and creates false greens.

`include_benign=false`: benign records are excluded from the default leak count
but remain in JSON with `status="benign"`. `include_benign=true`: they are included
in the report list and summary.

### 5.7 Confidence policy

- `high`: literal/simple alias or loop expansion, complete sender and slot.
- `medium`: lifetime heuristic or receiver inferred from a simple assignment.
- `low`: dynamic composition, cross-module, unknown receiver/connection type.

**Default `confidence = "low"`** so low-confidence items are not silently hidden.
The summary must always expose `by_confidence` counts, including `low`; the user
can raise the threshold to `medium`/`high` to reduce noise.

## 6. Output and CLI contract

### JSON

Always include the structured block; do **not** make it conditional on `--signals`.

Per module:

```json
{
  "research_metrics": {
    "qgis_context": {
      "signal_leaks": ["self.radio_gradient.toggled"],
      "signal_connections": {
        "summary": {
          "connect_sites": 80,
          "matched": 42,
          "unmatched": 16,
          "benign": 22,
          "by_confidence": {"high": 16, "medium": 6, "low": 0}
        },
        "items": [
          {
            "file": "gui/ui/pages/settings/symbology_tab.py",
            "line": 327,
            "scope": "SymbologyTab.connect_signals",
            "class_name": "SymbologyTab",
            "function_name": "connect_signals",
            "sender": "self.radio_gradient.toggled",
            "receiver": "self",
            "slot": "self.changed.emit",
            "status": "unmatched",
            "confidence": "high",
            "lifetime": null,
            "connection_type": "auto",
            "reason": "no matching disconnect in scope",
            "text": "signal.connect(self.changed.emit)"
          }
        ]
      }
    }
  }
}
```

Project aggregate:

```json
{
  "qgis_context_summary": {
    "signal_leaks": ["..."],
    "signal_connections": {
      "summary": {"connect_sites": 80, "matched": 42, "unmatched": 16, "benign": 22},
      "items": ["..."]
    }
  }
}
```

- Do **not** add a nested `schema_version`; the top-level
  `project_context.json` `schema_version` governs the contract.
- Keep `signal_leaks` as a deprecated, sorted list of unmatched sender strings for
  one minor release. It loses counts by design; `signal_connections.items` is the
  source of truth.
- Sort items by `(file, line, sender, slot, order)` for stable snapshots.

### CLI and human output

- Add `analyze --signals` (no `--verbose` alias unless one already exists).
- **Default human output:** one line, `ℹ️ Unmatched signal paths: N
  (informational; use --signals for details)`, never the 🚨 banner.
- `--signals`: print the full unmatched list with `file:line`, confidence and
  lifetime; still no gate by default.
- `PROJECT_SUMMARY.md`: counts only (including `by_confidence`); full items live in
  JSON. Do not flood the Markdown report.

## 7. Configuration

```toml
[tool.qgis-analyzer.profiles.default.rules.SIGNAL_LEAK]
emit = false              # opt-in gate; default informational
scope = "class"           # function | class | file
include_benign = false    # show benign lifetime entries
confidence = "low"        # minimum confidence to report (low shows all)
ignore_senders = []       # exact or simple glob, e.g. "self.dialog.preview_widget.*"
ignore_paths = []         # file globs, matched with IgnoreMatcher semantics
```

- `emit=true` produces a normal `SIGNAL_LEAK` issue with the configured severity
  **before scoring**. Add `SIGNAL_LEAK` to the explicit opt-in path for
  `scope="security"` (or document that `emit` is only honored in `all`).
- `ignore_paths` reuses the project `IgnoreMatcher`, not a separate glob dialect.
- `confidence` filters the human list and the legacy list; the JSON always keeps
  all items with their confidence.
- `ignore_senders` uses exact strings or simple `fnmatch` globs; no regex.

## 8. Test matrix

Add fixtures under `tests/fixtures/signal_leaks/` and golden JSON snapshots:

| Fixture | Expected |
| :--- | :--- |
| `direct_match.py` | 0 unmatched |
| `loop_disconnect.py` | 0 unmatched (D1 regression) |
| `alias_disconnect.py` | 0 unmatched |
| `loop_connect.py` | N unmatched (D7 regression) |
| `partial_slot.py` | 1 unmatched (one of two slots) |
| `duplicate_connect.py` | 1 duplicate after one disconnect |
| `disconnect_all.py` | `disconnect()` resolves every slot |
| `delete_later.py` | `benign` / `local_widget`, 0 leaks |
| `parent_child.py` | `benign` / `parent_child`, 0 leaks by default |
| `destroyed_hook.py` | `benign` / `destroyed_hook`, 0 leaks |
| `init_gui_unload.py` | resolved within the same class |
| `init_gui_no_unload.py` | unmatched, `confidence=high` |
| `cross_function.py` | unmatched by default; resolved with `scope="file"` |
| `cross_module.py` | unmatched, `confidence=low` |
| `unique_connection.py` | one connection, no duplicate |
| `config_ignore.py` | ignored sender/path produces no entry |
| `call_chain.py` | sender preserved as `self.iface.mapCanvas().xyCoordinates` (D9) |
| `keyword_connection.py` | `connect(slot, Qt.QueuedConnection)` parsed |
| `nested_scope.py` | nested classes/functions use distinct scopes |
| `reassigned_alias.py` | ambiguous alias is low confidence, not falsely resolved |

Additional requirements:

- Summary count equals `len(items)` with `status="unmatched"` (no unique-string
  dedupe); benign items are counted separately.
- The same fixture produces a byte-stable JSON snapshot across runs.
- Changing `include_benign`/`scope`/`confidence` must not require re-analysis of
  unchanged modules; exercise the cache.
- `emit=true` adds an issue before scoring and respects the configured scope.

The SecInterp corpus is useful for a **manual integration check**, not a CI
assertion: it lives in another repository and its 47/16 numbers are a snapshot of a
particular code state.

## 9. Acceptance criteria

- [ ] `SIGNAL_LEAK` is no longer described as "connected in `initGui` but not
      disconnected in `unload`"; docstrings/catalog describe the actual matcher.
- [ ] Loop-variable disconnects produce 0 false positives.
- [ ] Loop-variable connects produce the expected unmatched entries.
- [ ] Partial-slot disconnects report the remaining slot.
- [ ] Duplicate connections are counted, not collapsed.
- [ ] `deleteLater` / explicit parent-child / `destroyed` cleanup are `benign`
      only with evidence and are excluded from the default leak count.
- [ ] Every item has `file`, `line`, `scope`, `sender`, `receiver`, `slot`,
      `status`, `confidence`, `lifetime`, `connection_type`.
- [ ] `signal_connections` is always present in JSON; the human banner is opt-in.
- [ ] `signal_leaks` remains available (deprecated) for one minor release.
- [ ] `emit=true` produces a normal issue before scoring; default does not gate.
- [ ] `confidence=low` is visible in `by_confidence` and not silently dropped.
- [ ] Cache behavior is covered: config changes do not reuse stale resolved data.
- [ ] Tests/fixtures pass in CI; JSON snapshots are stable.
- [ ] CHANGELOG and README document the flag, config and JSON block.

## 10. Compatibility and migration

- **Minor version (`1.19.0`)**: add `signal_connections`, keep `signal_leaks`,
  add `--signals`, add config. No breaking change.
- **Next major**: remove `signal_leaks` or make it an alias of the unmatched
  sender list; change the default summary display if needed.
- Consumers that read `qgis_context.signal_leaks` keep working.
- Do not change CC, i18n, security or module-size semantics.
- The default human banner changes from 🚨 to an informational one-liner; document
  it in the CHANGELOG as a presentation change.

## 11. Non-goals

- Full dataflow analysis, SSA, type inference or runtime instrumentation.
- Cross-repository/plugin signal buses resolved across modules by default.
- Proving that a `disconnect` is reachable at runtime.
- Replacing Qt's own object-lifetime model.
- Turning `SIGNAL_LEAK` into a release gate for every plugin.
- `getattr`, dict/list indexing, `QObject.disconnect` static forms or dynamic
  `sender()`/`receiver()` resolution; these stay low confidence/unsupported.

## 12. Implementation checklist / PR breakdown

**PR 1 — honest contract (no algorithm change)**
- [ ] Rename the summary label to "Unmatched connect/disconnect paths
      (informational)" and stop the unconditional 🚨 banner.
- [ ] Add `--signals` for the full human list; default one informational line.
- [ ] Fix `SafetyVisitor`/catalog docstrings.
- [ ] Add the JSON skeleton with legacy literal data only if it is clearly marked
      unstable; otherwise defer `signal_connections` to PR 2 to avoid changing its
      shape twice.
- [ ] Keep `signal_leaks`; tests for the label/flag.

**PR 2 — collector + resolver**
- [ ] Add `signal_analysis.py` (or a dedicated visitor) with `SignalEvent`,
      collector, canonicalizer and resolver.
- [ ] Per-scope symbol table, alias/loop expansion, receiver/slot identity.
- [ ] Slot-aware matching, duplicate counting, connection types.
- [ ] Project-level resolver before scoring; JSON and `--signals`.
- [ ] Fixtures for D1, D2, D3, D5, D7, D9, D10, D11.

**PR 3 — lifetime**
- [ ] Evidence-based `deleteLater`, parent-child and `destroyed` classification.
- [ ] `include_benign` and `confidence` config.
- [ ] Fixtures for D6; cache/config tests.

**PR 4 — optional cross-module**
- [ ] Detect connect in module A / disconnect in module B; `confidence=low`.
- [ ] Never resolve by default; document the limitation.

## 13. SecInterp expected outcome

| State | `unmatched` | `benign` | Notes |
| :--- | ---: | ---: | :--- |
| Current analyzer + current code | 47 unique strings (16 real sites, 13 hidden) | not modelled | Misleading banner |
| Improved analyzer + current code | **16** | 22 | Real bug visible |
| Improved analyzer + SecInterp P0 | **0** | 22 | Duplication fixed |
| Improved analyzer + SecInterp P0 + P1 | **0** | 0 | Panel/selector wiring moved to lifecycle |

The 16 are 15 `source → self.changed.emit` connections in
`symbology_tab.py:326-343` plus `btn_reset_units.clicked` in
`symbology_units.py:127`.

These numbers are a target for a manual integration run, not a hard-coded CI
assertion.

## 14. References

- `analyzer/visitors/safety_visitor.py` (`visit_Call`, `_get_full_attribute_name`,
  `signal_leaks`).
- `analyzer/rules/catalog_core.py` (`SIGNAL_LEAK`).
- `analyzer/aggregators.py` (`get_research_summary`).
- `analyzer/reporters/summary_reporter.py`.
- `analyzer/visitors/composite_visitor.py` (`qgis_context`).
- `analyzer/visitors/base.py` (`rules_config`, `_report_issue`).
- `tests/test_safety.py`.
- SecInterp fix plan:
  [implementation_plan_v3.12.1_signal_idempotency.md](implementation_plan_v3.12.1_signal_idempotency.md).
