"""Tests for the unified rule registry and its anti-drift guarantees."""

import ast
import pathlib
import re
import unittest

import analyzer
from analyzer.rules import RULE_CATALOG, categories, get_rule, get_rules, rules_for_scope
from analyzer.rules.catalog import CATEGORY_ORDER
from analyzer.rules.catalog_metadata import METADATA_RULE_IDS
from analyzer.rules.qgis_rules import get_qgis_audit_rules
from analyzer.rules.render import render_list_rules_text, render_rules_md
from analyzer.rules.scopes import SCOPE_RULES
from analyzer.secrets import SecretScanner
from analyzer.security_checker import SecurityRegistry
from analyzer.visitors.qt_transition_visitor import QT6_REMOVED_NAMES

_ANALYZER_DIR = pathlib.Path(analyzer.__file__).resolve().parent
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
_CATEGORY_KEYS = {key for key, _, _, _ in CATEGORY_ORDER}
_VALID_SEVERITIES = {"high", "medium", "low"}

# The only files allowed to contain dynamic (non-literal) ``_report_issue`` calls
# (fed by ``QT6_REMOVED_NAMES``); the exact count is pinned too.
_DYNAMIC_FILES = {"qt_transition_visitor.py"}
_EXPECTED_DYNAMIC_COUNT = 2


def _string_constants(node: ast.AST) -> set[str]:
    """Collect string constants from a node, including both ternary branches."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.IfExp):
        return _string_constants(node.body) | _string_constants(node.orelse)
    return set()


def _scan_security_ids() -> set[str]:
    """AST-extract the ``id=`` values of ``SecurityFinding(...)`` calls."""
    source = (_ANALYZER_DIR / "security_rules.py").read_text(encoding="utf-8")
    ids: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "SecurityFinding":
            for keyword in node.keywords:
                if keyword.arg == "id":
                    ids |= _string_constants(keyword.value)
    return ids


def _scan_report_issue() -> tuple[set[str], set[tuple[str, int]]]:
    """AST-scan the analyzer for ``_report_issue`` call sites.

    Returns:
        ``(literal_ids, dynamic_sites)`` where ``literal_ids`` are the string
        literals passed as the first argument and ``dynamic_sites`` are the
        ``(filename, lineno)`` of non-literal first arguments.
    """
    literal: set[str] = set()
    dynamic: set[tuple[str, int]] = set()
    for path in _ANALYZER_DIR.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "_report_issue"):
                continue
            first = node.args[0] if node.args else None
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                literal.add(first.value)
            else:
                dynamic.add((path.name, node.lineno))
    return literal, dynamic


class TestCatalogSchema(unittest.TestCase):
    def test_ids_are_unique(self):
        ids = [rule.id for rule in RULE_CATALOG.values()]

        self.assertEqual(len(ids), len(set(ids)))

    def test_emitted_severities_are_valid(self):
        for rule in get_rules():
            self.assertIn(rule.severity, _VALID_SEVERITIES, rule.id)

    def test_categories_are_valid(self):
        for rule in RULE_CATALOG.values():
            self.assertIn(rule.category, _CATEGORY_KEYS, rule.id)

    def test_get_rule(self):
        self.assertIsNotNone(get_rule("MISSING_I18N"))
        self.assertIsNone(get_rule("NOT_A_REAL_RULE"))

    def test_helpers(self):
        self.assertEqual(len(categories()), len(CATEGORY_ORDER))
        self.assertEqual(rules_for_scope("i18n"), {"MISSING_I18N"})
        self.assertEqual(rules_for_scope("nonexistent"), set())


class TestScopeParity(unittest.TestCase):
    _EXPECTED = {
        "i18n": {"MISSING_I18N"},
        "security": {
            "UNSAFE_SUBPROCESS",
            "B102",
            "B301",
            "B307",
            "B602",
            "B608",
            "HARDCODED_SECRET",
            "AWS_KEY",
            "GOOGLE_API_KEY",
            "TWILIO_KEY",
            "GENERIC_SECRET",
            "HIGH_ENTROPY",
        },
        "performance": {
            "SPATIAL_INDEX",
            "BLOCKING_NETWORK_CALL",
            "UI_BLOCKING_LOOP",
            "NON_PYTHONIC_LOOP",
        },
        "architecture": {
            "QGIS_PROTECTED_MEMBER",
            "GDAL_DIRECT_IMPORT",
            "QGIS_LEGACY_IMPORT",
            "HEAVY_LOGIC_UI",
            "PYQT5_IMPORT",
            "LEGACY_GDAL_IMPORT",
            "QT6_QAPP_USAGE",
            "QT6_QREGEXP_USAGE",
            "QT6_QDESKTOPWIDGET",
            "QT6_REMOVED_ENUM",
            "QT6_QFONTMETRICS_WIDTH",
            "QT6_QCOMBOBOX_ACTIVATED",
            "QT6_COMPILED_RESOURCES",
            "QT6_ADDACTION_MULTIARG",
            "QT6_QVARIANT_NULL",
            "QT6_QDATETIME_ARGS",
            "QT6_QDATETIME_QDATE",
        },
        "metadata": {
            "MANDATORY_CLEANUP",
            "OBSOLETE_API",
            "IFACE_AS_ARGUMENT",
            "METADATA_REPOSITORY",
            "METADATA_VERSION",
            "METADATA_QGIS4",
            "METADATA_SUPPORTS_QT6",
            "METADATA_CATEGORY",
        },
    }

    def test_scope_rules_match_pre_change_snapshot(self):
        self.assertEqual(SCOPE_RULES, self._EXPECTED)


class TestIdCoverage(unittest.TestCase):
    def test_catalog_covers_every_emission_channel(self):
        literal, dynamic = _scan_report_issue()

        self.assertEqual({name for name, _ in dynamic}, _DYNAMIC_FILES)
        self.assertEqual(len(dynamic), _EXPECTED_DYNAMIC_COUNT)
        self.assertTrue(SecurityRegistry.rule_ids(), "security registry is empty")
        self.assertEqual(_scan_security_ids(), SecurityRegistry.rule_ids())

        extracted = (
            literal
            | set(QT6_REMOVED_NAMES)
            | {rule["id"] for rule in get_qgis_audit_rules()}
            | SecurityRegistry.rule_ids()
            | SecretScanner.rule_ids()
            | METADATA_RULE_IDS
        )
        emitted = {rule.id for rule in get_rules()}

        self.assertEqual(extracted, emitted)

    def test_regex_severity_matches_catalog(self):
        for rule in get_qgis_audit_rules():
            catalog = get_rule(rule["id"])
            self.assertIsNotNone(catalog, rule["id"])
            assert catalog is not None  # for type checkers
            self.assertEqual(catalog.severity, rule["severity"], rule["id"])


class TestRenders(unittest.TestCase):
    def test_rules_md_is_in_sync(self):
        current = (_PROJECT_ROOT / "RULES.md").read_text(encoding="utf-8")

        self.assertEqual(render_rules_md(), current)

    def test_rules_md_render_is_deterministic(self):
        self.assertEqual(render_rules_md(), render_rules_md())

    def test_list_rules_text_lists_every_rule(self):
        text = render_list_rules_text()

        for rule in get_rules():
            self.assertIn(rule.id, text)

        parsed = set(re.findall(r"^- \[(?:HIGH|MEDIUM|LOW)\] (\w+):", text, re.MULTILINE))
        self.assertEqual(parsed, {rule.id for rule in get_rules()})


class TestRuntimeGuard(unittest.TestCase):
    def test_unknown_rule_warns_only_once(self):
        from analyzer.visitors import base

        unknown = "ZZZ_UNKNOWN_TEST_RULE"
        base._WARNED_RULE_IDS.discard(unknown)
        visitor = base.BaseVisitor("x.py", scope="all")

        with self.assertLogs("qgis_analyzer", level="WARNING") as captured:
            visitor._report_issue(unknown, 1, "m")
            visitor._report_issue(unknown, 2, "m")

        self.assertEqual(len(captured.records), 1)
        self.assertIn(unknown, base._WARNED_RULE_IDS)


if __name__ == "__main__":
    unittest.main()
