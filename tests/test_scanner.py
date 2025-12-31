import unittest
import pathlib
import tempfile
import shutil
from src.analyzer.scanner import audit_qgis_standards
from src.analyzer.validators import validate_metadata, validate_plugin_structure


class TestScanner(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for each test
        self.test_dir = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_validate_plugin_structure(self):
        # Setup: Create a fake plugin structure
        (self.test_dir / "metadata.txt").write_text("name=Test", encoding="utf-8")
        (self.test_dir / "__init__.py").write_text("def classFactory(): pass", encoding="utf-8")
        (self.test_dir / "LICENSE").write_text("GPL", encoding="utf-8")

        result = validate_plugin_structure(self.test_dir)
        self.assertTrue(result["is_valid"])
        self.assertTrue(result["files"]["metadata.txt"])
        self.assertTrue(result["has_class_factory"])

    def test_validate_plugin_structure_missing_file(self):
        (self.test_dir / "__init__.py").write_text("def classFactory(): pass", encoding="utf-8")

        result = validate_plugin_structure(self.test_dir)
        self.assertFalse(result["is_valid"])
        self.assertFalse(result["files"]["metadata.txt"])

    def test_validate_metadata(self):
        metadata_content = """
[general]
name=Test Plugin
description=A description
version=0.1
qgisMinimumVersion=3.0
author=Tester
email=test@test.com
"""
        meta_file = self.test_dir / "metadata.txt"
        meta_file.write_text(metadata_content, encoding="utf-8")

        result = validate_metadata(self.test_dir / "metadata.txt")
        self.assertTrue(result["is_valid"])
        self.assertEqual(len(result["missing"]), 0)

    def test_validate_metadata_missing_fields(self):
        meta_file = self.test_dir / "metadata.txt"
        meta_file.write_text("name=Test\nversion=0.1", encoding="utf-8")

        result = validate_metadata(self.test_dir)
        self.assertFalse(result["is_valid"])
        self.assertIn("description", result["missing"])

    def test_audit_qgis_standards(self):
        py_content = """
layer = mapLayersByName("test")[0]
QIcon("icons/my_icon.png")
print("debug")
"""
        py_file = self.test_dir / "test_plugin.py"
        py_file.write_text(py_content, encoding="utf-8")

        modules_data = [{"path": "test_plugin.py"}]
        results = audit_qgis_standards(modules_data, self.test_dir)

        issue_types = [i["type"] for i in results["issues"]]
        self.assertIn("UNPRECISE_LAYER", issue_types)
        self.assertIn("MANUAL_RESOURCE_PATH", issue_types)
        self.assertIn("PRINT_STATEMENT", issue_types)


if __name__ == "__main__":
    unittest.main()
