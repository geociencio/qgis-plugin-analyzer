"""Tests for the catalog-backed METADATA_* rules."""

import pathlib
import tempfile
import unittest
from unittest.mock import patch

from analyzer.metadata_audit import METADATA_RULE_IDS, audit_metadata_rules
from analyzer.qgis_checks import run_qgis_checks

_VALID = """\
[general]
name=Demo
description=Demo plugin
version=1.2.3
qgisMinimumVersion=3.28
qgisMaximumVersion=4.0
author=Demo
email=demo@example.com
about=Demo
repository=https://example.com/demo
category=Vector
"""


class TestMetadataRules(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, text: str) -> pathlib.Path:
        path = self.root / "metadata.txt"
        path.write_text(text, encoding="utf-8")
        return path

    def test_valid_metadata_has_no_findings(self):
        findings = audit_metadata_rules(self._write(_VALID))

        self.assertEqual(findings, [])

    def test_qgis_maximum_accepts_patch_version(self):
        text = _VALID.replace("qgisMaximumVersion=4.0", "qgisMaximumVersion=4.0.0")

        self.assertEqual(audit_metadata_rules(self._write(text)), [])

    def test_all_rules_are_reported(self):
        path = self._write(
            "[general]\nname=Demo\nversion=1.0\nqgisMaximumVersion=3.40\nsupportsQt6=True\n"
        )

        found = {finding["type"] for finding in audit_metadata_rules(path)}

        self.assertEqual(found, set(METADATA_RULE_IDS))
        self.assertTrue(
            all(finding["file"] == "metadata.txt" for finding in audit_metadata_rules(path))
        )

    def test_missing_file_has_no_findings(self):
        self.assertEqual(audit_metadata_rules(self.root / "missing.txt"), [])

    def test_qgis_checks_respects_metadata_rules_flag(self):
        self._write(
            _VALID.replace("repository=https://example.com/demo\n", "").replace(
                "category=Vector\n", ""
            )
        )
        (self.root / "__init__.py").write_text("", encoding="utf-8")
        discovery = {"total_size_mb": 0.0, "binaries": []}

        with patch("analyzer.qgis_checks.validate_metadata_urls", return_value={}):
            included = run_qgis_checks([], self.root, {}, discovery, metadata_rules=True)
            excluded = run_qgis_checks([], self.root, {}, discovery, metadata_rules=False)

        included_ids = {issue["type"] for issue in included["compliance"]["issues"]}
        excluded_ids = {issue["type"] for issue in excluded["compliance"]["issues"]}
        self.assertTrue({"METADATA_REPOSITORY", "METADATA_CATEGORY"} <= included_ids)
        self.assertFalse(METADATA_RULE_IDS & excluded_ids)


if __name__ == "__main__":
    unittest.main()
