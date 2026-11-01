"""Tests for the signal collector and project-level resolver."""

import ast
import pathlib
import tempfile
import textwrap
import unittest

from analyzer.signal_analysis import collect_signal_events
from analyzer.signal_resolver import aggregate_signal_reports, report_for_file, resolve_signals


def _events(code: str, file: str = "a.py") -> list[dict]:
    return collect_signal_events(ast.parse(textwrap.dedent(code)), file)


def _report(code: str, **kwargs) -> dict:
    return resolve_signals(_events(code), **kwargs)


class TestSignalCollection(unittest.TestCase):
    def test_direct_match(self):
        report = _report(
            """
            class Plugin:
                def initGui(self):
                    self.btn.clicked.connect(self.on_click)
                def unload(self):
                    self.btn.clicked.disconnect(self.on_click)
            """
        )

        self.assertEqual(report["summary"]["matched"], 1)
        self.assertEqual(report["summary"]["unmatched"], 0)

    def test_loop_disconnect_is_resolved(self):
        report = _report(
            """
            class Plugin:
                def f(self):
                    self.a.toggled.connect(self.on_a)
                    self.b.toggled.connect(self.on_b)
                    for signal in (self.a.toggled, self.b.toggled):
                        signal.disconnect()
            """
        )

        self.assertEqual(report["summary"]["unmatched"], 0)

    def test_loop_connect_expands_to_each_signal(self):
        report = _report(
            """
            class Plugin:
                def f(self):
                    for signal in (self.a.toggled, self.b.toggled):
                        signal.connect(self.changed.emit)
            """
        )

        self.assertEqual(report["summary"]["connect_sites"], 2)
        self.assertEqual(report["summary"]["unmatched"], 2)

    def test_alias_disconnect(self):
        report = _report(
            """
            class Plugin:
                def initGui(self):
                    widget = self.dialog.preview
                    widget.clicked.connect(self.on_click)
                def unload(self):
                    widget = self.dialog.preview
                    widget.clicked.disconnect(self.on_click)
            """
        )

        self.assertEqual(report["summary"]["matched"], 1)
        self.assertEqual(report["summary"]["unmatched"], 0)

    def test_call_chain_is_preserved(self):
        events = _events(
            """
            class Plugin:
                def f(self):
                    self.iface.mapCanvas().xyCoordinates.connect(self.on_xy)
            """
        )

        self.assertEqual(events[0]["sender"], "self.iface.mapCanvas().xyCoordinates")

    def test_partial_slot_disconnect_leaves_one_unmatched(self):
        report = _report(
            """
            class Plugin:
                def f(self):
                    self.radio.toggled.connect(self.on_a)
                    self.radio.toggled.connect(self.on_b)
                    self.radio.toggled.disconnect(self.on_a)
            """
        )

        self.assertEqual(report["summary"]["matched"], 1)
        self.assertEqual(report["summary"]["unmatched"], 1)

    def test_duplicate_connect_is_counted(self):
        report = _report(
            """
            class Plugin:
                def f(self):
                    self.btn.clicked.connect(self.on_click)
                    self.btn.clicked.connect(self.on_click)
                    self.btn.clicked.disconnect(self.on_click)
            """
        )

        self.assertEqual(report["summary"]["connect_sites"], 2)
        self.assertEqual(report["summary"]["unmatched"], 1)

    def test_slotless_disconnect_only_matches_its_sender(self):
        report = _report(
            """
            class Plugin:
                def f(self):
                    self.a.toggled.connect(self.changed.emit)
                    self.b.toggled.connect(self.changed.emit)
                    self.changed.disconnect()
            """
        )

        self.assertEqual(report["summary"]["matched"], 0)
        self.assertEqual(report["summary"]["unmatched"], 2)

    def test_disconnect_without_slot_consumes_all(self):
        report = _report(
            """
            class Plugin:
                def f(self):
                    self.radio.toggled.connect(self.on_a)
                    self.radio.toggled.connect(self.on_b)
                    self.radio.toggled.disconnect()
            """
        )

        self.assertEqual(report["summary"]["unmatched"], 0)

    def test_tuple_unpacked_loop_disconnect(self):
        report = _report(
            """
            class Plugin:
                def connect_signals(self):
                    self.raster.layerChanged.connect(self.band.setLayer)
                def disconnect_signals(self):
                    for signal, slot in ((self.raster.layerChanged, self.band.setLayer),):
                        signal.disconnect(slot)
            """
        )

        self.assertEqual(report["summary"]["matched"], 1)
        self.assertEqual(report["summary"]["unmatched"], 0)

    def test_unique_connection_is_deduplicated(self):
        report = _report(
            """
            class Plugin:
                def f(self):
                    self.btn.clicked.connect(self.on_click, Qt.UniqueConnection)
                    self.btn.clicked.connect(self.on_click, Qt.UniqueConnection)
            """
        )

        self.assertEqual(report["summary"]["connect_sites"], 1)
        self.assertEqual(report["summary"]["unmatched"], 1)


class TestSignalScopes(unittest.TestCase):
    def test_class_scope_matches_init_and_unload(self):
        report = _report(
            """
            class Plugin:
                def __init__(self):
                    self.btn.clicked.connect(self.on_click)
                def unload(self):
                    self.btn.clicked.disconnect(self.on_click)
            """
        )

        self.assertEqual(report["summary"]["matched"], 1)

    def test_function_scope_requires_same_function(self):
        report = _report(
            """
            class Plugin:
                def __init__(self):
                    self.btn.clicked.connect(self.on_click)
                def unload(self):
                    self.btn.clicked.disconnect(self.on_click)
            """,
            scope="function",
        )

        self.assertEqual(report["summary"]["unmatched"], 1)

    def test_file_scope_matches_across_classes(self):
        report = _report(
            """
            class A:
                def f(self):
                    self.btn.clicked.connect(self.on_click)
            class B:
                def g(self):
                    self.btn.clicked.disconnect(self.on_click)
            """,
            scope="file",
        )

        self.assertEqual(report["summary"]["matched"], 1)

    def test_cross_module_is_low_confidence(self):
        events = _events(
            """
            class Plugin:
                def f(self):
                    self.btn.clicked.connect(self.on_click)
            """,
            file="a.py",
        )
        events += _events(
            """
            class Plugin:
                def g(self):
                    self.btn.clicked.disconnect(self.on_click)
            """,
            file="b.py",
        )

        report = resolve_signals(events)

        self.assertEqual(report["summary"]["unmatched"], 1)
        self.assertEqual(report["items"][0]["confidence"], "low")
        self.assertIn("cross-module", report["items"][0]["reason"])


class TestSignalLifetime(unittest.TestCase):
    def test_delete_later_is_benign(self):
        report = _report(
            """
            class Plugin:
                def f(self):
                    row = UnitStyleEditor(self)
                    row.color_requested.connect(self.changed.emit)
                    row.deleteLater()
            """
        )

        self.assertEqual(report["summary"]["benign"], 1)
        self.assertEqual(report["summary"]["unmatched"], 0)
        self.assertEqual(report["items"][0]["lifetime"], "local_widget")

    def test_explicit_parent_is_benign(self):
        report = _report(
            """
            class Plugin:
                def f(self):
                    self.row = QWidget(self)
                    self.row.clicked.connect(self.on_click)
            """
        )

        self.assertEqual(report["summary"]["benign"], 1)
        self.assertEqual(report["items"][0]["lifetime"], "parent_child")

    def test_disposed_container_makes_child_widgets_benign(self):
        report = _report(
            """
            class UnitStyleEditor:
                def __init__(self):
                    self.check.toggled.connect(self.visibility_changed.emit)
            class UnitsEditor:
                def rebuild(self):
                    row = UnitStyleEditor(self)
                    row.deleteLater()
            """
        )

        self.assertEqual(report["summary"]["benign"], 1)
        self.assertEqual(report["items"][0]["lifetime"], "local_widget")

    def test_explicit_parent_panel_is_benign(self):
        report = _report(
            """
            class SidePanel:
                def __init__(self, parent):
                    self.parent = parent
            class MainDialog:
                def init(self):
                    self.panel = SidePanel(self)
                    self.panel.changed.connect(self.on_changed)
            """
        )

        self.assertEqual(report["summary"]["benign"], 1)
        self.assertEqual(report["items"][0]["lifetime"], "parent_child")

    def test_self_attribute_without_lifetime_evidence_is_not_benign(self):
        report = _report(
            """
            class Plugin:
                def f(self):
                    self.row = SomeWidget()
                    self.row.clicked.connect(self.on_click)
            """
        )

        self.assertEqual(report["summary"]["benign"], 0)
        self.assertEqual(report["summary"]["unmatched"], 1)


class TestSignalReporting(unittest.TestCase):
    def test_ignore_senders_and_paths(self):
        events = _events(
            """
            class Plugin:
                def f(self):
                    self.btn.clicked.connect(self.on_click)
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            report = resolve_signals(
                events,
                ignore_senders=["self.btn.*"],
                ignore_paths=["a.py"],
                project_root=root,
            )

        self.assertEqual(report["summary"]["connect_sites"], 0)

    def test_report_for_file_and_aggregate(self):
        events = _events(
            """
            class Plugin:
                def f(self):
                    self.btn.clicked.connect(self.on_click)
            """
        )
        report = resolve_signals(events)
        module = {
            "path": "a.py",
            "research_metrics": {"qgis_context": {"signal_connections": report}},
        }

        file_report = report_for_file(report, "a.py")
        aggregate = aggregate_signal_reports([module])

        self.assertEqual(file_report["summary"]["unmatched"], 1)
        self.assertIsNotNone(aggregate)
        assert aggregate is not None
        self.assertEqual(aggregate["summary"]["unmatched"], 1)


if __name__ == "__main__":
    unittest.main()
