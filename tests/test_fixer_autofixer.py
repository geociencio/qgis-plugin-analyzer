"""Tests for the auto-fix engine (git status, diff, handlers and AutoFixer)."""

import contextlib
import io
import pathlib
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from analyzer.fixer import AutoFixer, check_git_status, create_ast_handler, registry, show_diff
from analyzer.transformers import GDALImportTransformer


class TestHelpers(unittest.TestCase):
    @patch("analyzer.fixer.subprocess.run")
    def test_check_git_status_clean(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        self.assertTrue(check_git_status(pathlib.Path("/tmp")))

    @patch("analyzer.fixer.subprocess.run")
    def test_check_git_status_dirty(self, mock_run):
        mock_run.return_value = MagicMock(stdout=" M file.py\n", returncode=0)
        self.assertFalse(check_git_status(pathlib.Path("/tmp")))

    @patch("analyzer.fixer.subprocess.run", side_effect=FileNotFoundError)
    def test_check_git_status_no_git(self, _mock_run):
        self.assertTrue(check_git_status(pathlib.Path("/tmp")))

    def test_show_diff_prints_unified_diff(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            show_diff(pathlib.Path("m.py"), "a = 1\n", "a = 2\n")

        self.assertIn("-a = 1", out.getvalue())
        self.assertIn("+a = 2", out.getvalue())


class TestCreateAstHandler(unittest.TestCase):
    def test_mismatched_issue_type_is_not_applied(self):
        handler = create_ast_handler("GDAL_DIRECT_IMPORT", GDALImportTransformer, "msg")
        ctx = {
            "issue": {"type": "OTHER"},
            "content": "import gdal\n",
            "dry_run": False,
        }

        self.assertFalse(handler(ctx)["applied"])

    def test_dry_run_reports_applied_without_content(self):
        handler = create_ast_handler("GDAL_DIRECT_IMPORT", GDALImportTransformer, "msg")
        ctx = {"issue": {"type": "GDAL_DIRECT_IMPORT"}, "content": "import gdal\n", "dry_run": True}

        result = handler(ctx)

        self.assertTrue(result["applied"])
        self.assertIsNone(result["new_content"])

    def test_applies_transformation(self):
        handler = create_ast_handler("GDAL_DIRECT_IMPORT", GDALImportTransformer, "msg")
        ctx = {
            "issue": {"type": "GDAL_DIRECT_IMPORT"},
            "content": "import gdal\n",
            "dry_run": False,
        }

        result = handler(ctx)

        self.assertTrue(result["applied"])
        self.assertIn("from osgeo import gdal", result["new_content"])


class TestAutoFixer(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        (self.root / "mod.py").write_text("import gdal\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_get_fixable_issues_filters_unknown(self):
        fixer = AutoFixer(self.root, dry_run=True)
        issues = [
            {"type": "GDAL_DIRECT_IMPORT", "file": "mod.py"},
            {"type": "UNKNOWN", "file": "mod.py"},
        ]

        fixable = fixer.get_fixable_issues(issues)

        self.assertEqual(len(fixable), 1)
        self.assertIn("handler", fixable[0])

    def test_apply_fixes_dry_run(self):
        fixer = AutoFixer(self.root, dry_run=True)
        issues = fixer.get_fixable_issues([{"type": "GDAL_DIRECT_IMPORT", "file": "mod.py"}])

        with contextlib.redirect_stdout(io.StringIO()):
            stats = fixer.apply_fixes(issues, interactive=False)

        self.assertEqual(stats["applied"], 1)
        self.assertIn("import gdal", (self.root / "mod.py").read_text(encoding="utf-8"))

    @patch("analyzer.fixer.check_git_status", return_value=True)
    def test_apply_fixes_writes_file(self, _mock_git):
        fixer = AutoFixer(self.root, dry_run=False)
        handler = registry.get_handler("GDAL_DIRECT_IMPORT")
        issues = [
            {
                "type": "GDAL_DIRECT_IMPORT",
                "file": "mod.py",
                "line": 1,
                "handler": handler,
                "fix_description": "replace",
            }
        ]

        with contextlib.redirect_stdout(io.StringIO()):
            stats = fixer.apply_fixes(issues, interactive=False)

        self.assertEqual(stats["applied"], 1)
        self.assertIn("from osgeo import gdal", (self.root / "mod.py").read_text(encoding="utf-8"))

    def test_apply_fixes_missing_file_counts_failed(self):
        fixer = AutoFixer(self.root, dry_run=False)
        issues = [{"type": "GDAL_DIRECT_IMPORT", "file": "missing.py", "handler": lambda ctx: None}]

        with (
            contextlib.redirect_stdout(io.StringIO()),
            patch("analyzer.fixer.check_git_status", return_value=True),
        ):
            stats = fixer.apply_fixes(issues, interactive=False)

        self.assertEqual(stats["failed"], 1)


if __name__ == "__main__":
    unittest.main()
