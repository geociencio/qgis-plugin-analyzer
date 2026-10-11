"""Regression tests: boundary functions must accept both str and pathlib.Path."""

import pathlib
import tempfile
import unittest

from analyzer.scanner import analyze_module_worker


class TestPathNormalization(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        (self.root / "mod.py").write_text("def foo(x):\n    return x\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_analyze_module_worker_accepts_str(self):
        result = analyze_module_worker(str(self.root / "mod.py"), str(self.root))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertGreater(result["file_size_kb"], 0)

    def test_analyze_module_worker_accepts_path(self):
        result = analyze_module_worker(self.root / "mod.py", self.root)

        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
