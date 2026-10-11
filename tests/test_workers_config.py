"""Tests for configurable worker count and file batching."""

import os
import pathlib
import tempfile
import unittest

from analyzer.engine import ProjectAnalyzer


class TestResolveMaxWorkers(unittest.TestCase):
    def test_explicit_value_is_clamped_to_ceiling(self):
        self.assertEqual(ProjectAnalyzer._resolve_max_workers(8), 4)

    def test_explicit_zero_becomes_one(self):
        self.assertEqual(ProjectAnalyzer._resolve_max_workers(0), 1)

    def test_explicit_value_within_range(self):
        self.assertEqual(ProjectAnalyzer._resolve_max_workers(2), 2)

    def test_default_uses_cpu_minus_one_capped(self):
        cpu = os.cpu_count() or 4
        self.assertEqual(ProjectAnalyzer._resolve_max_workers(None), min(4, max(1, cpu - 1)))


class TestWorkersConfigAndChunking(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.out = self.root / "out"
        (self.root / "pyproject.toml").write_text(
            "[tool.qgis-analyzer.profiles.default]\nworkers = 2\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_workers_read_from_profile(self):
        analyzer = ProjectAnalyzer(str(self.root), output_dir=str(self.out))

        self.assertEqual(analyzer.max_workers, 2)

    def test_cli_workers_override_profile(self):
        analyzer = ProjectAnalyzer(str(self.root), output_dir=str(self.out), workers=1)

        self.assertEqual(analyzer.max_workers, 1)

    def test_chunk_files_covers_every_file(self):
        analyzer = ProjectAnalyzer(str(self.root), output_dir=str(self.out))
        analyzer.max_workers = 2
        files = [pathlib.Path(f"f{i}.py") for i in range(40)]

        chunks = analyzer._chunk_files(files)

        self.assertGreater(len(chunks), 1)
        self.assertEqual([f for chunk in chunks for f in chunk], files)

    def test_chunk_files_empty(self):
        analyzer = ProjectAnalyzer(str(self.root), output_dir=str(self.out))

        self.assertEqual(analyzer._chunk_files([]), [])


if __name__ == "__main__":
    unittest.main()
