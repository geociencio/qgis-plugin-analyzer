import pathlib
import shutil
import tempfile
import unittest

from analyzer.validators import (
    calculate_package_size,
    scan_for_binaries,
    validate_metadata,
    validate_metadata_urls,
    validate_plugin_structure,
)


class TestValidators(unittest.TestCase):
    """Unit tests for QGIS artifact validators and package metrics."""

    def setUp(self) -> None:
        """Sets up a temporary directory for each test."""
        self.test_dir = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Cleans up temporary resources."""
        shutil.rmtree(self.test_dir)

    def test_scan_for_binaries(self):
        # Create dummy binary files
        (self.test_dir / "lib").mkdir()
        (self.test_dir / "lib" / "test.dll").write_text("fake dll")
        (self.test_dir / "tool.exe").write_text("fake exe")
        (self.test_dir / "script.py").write_text("# python file")

        binaries = scan_for_binaries(self.test_dir)

        self.assertEqual(len(binaries), 2)
        self.assertTrue(any("test.dll" in b for b in binaries))
        self.assertTrue(any("tool.exe" in b for b in binaries))
        self.assertFalse(any("script.py" in b for b in binaries))

    def test_calculate_package_size(self):
        # Create files with known sizes
        (self.test_dir / "file1.txt").write_text("a" * 1024)  # 1KB
        (self.test_dir / "file2.txt").write_text("b" * 1024 * 1024)  # 1MB

        size_mb = calculate_package_size(self.test_dir)

        # Should be approximately 1.001 MB
        self.assertGreater(size_mb, 1.0)
        self.assertLess(size_mb, 1.1)

    def test_validate_metadata_urls_invalid(self):
        metadata = {
            "homepage": "not-a-url",
            "tracker": "",
            "repository": "https://github.com/user/repo",
        }

        # Mock test - in real scenario this would make HTTP requests
        # For unit test, we just verify the function signature
        result = validate_metadata_urls(metadata)

        self.assertIsInstance(result, dict)
        # Invalid URL should be marked as 'invalid'
        self.assertEqual(result.get("not-a-url"), "invalid")

    def test_validate_plugin_structure(self):
        # Valid structure
        (self.test_dir / "__init__.py").write_text("def classFactory(): pass")
        (self.test_dir / "metadata.txt").write_text("name=Test")
        (self.test_dir / "LICENSE").write_text("GPL")
        (self.test_dir / "plugin.py").write_text("")

        result = validate_plugin_structure(self.test_dir)

        self.assertTrue(result["is_valid"])
        self.assertEqual(len(result["missing_files"]), 0)
        self.assertTrue(result["has_python_files"])

    def test_validate_plugin_structure_missing_files(self):
        # Missing required files
        result = validate_plugin_structure(self.test_dir)

        self.assertFalse(result["is_valid"])
        self.assertIn("__init__.py", result["missing_files"])
        self.assertIn("metadata.txt", result["missing_files"])

    def test_validate_metadata(self):
        metadata_content = """name=Test Plugin
description=A test plugin
version=1.0.0
qgisMinimumVersion=3.0
author=Test Author
email=test@example.com
"""
        metadata_file = self.test_dir / "metadata.txt"
        metadata_file.write_text(metadata_content)

        result = validate_metadata(metadata_file)

        self.assertTrue(result["is_valid"])
        self.assertEqual(len(result["missing"]), 0)
        self.assertEqual(result["metadata"]["name"], "Test Plugin")


if __name__ == "__main__":
    unittest.main()
