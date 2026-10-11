"""Integration tests for the incremental per-file analysis cache."""

import dataclasses
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from analyzer.engine import ProjectAnalyzer
from analyzer.module_cache import (
    CACHE_FILENAME,
    ModuleCache,
    cache_signature,
    file_content_hash,
)
from analyzer.parallel_analysis import run_parallel_analysis

_VERSION = "test-version"


def _write_project(root: pathlib.Path) -> None:
    pkg = root / "pkg"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    (pkg / "b.py").write_text("def b():\n    return 2\n", encoding="utf-8")


class _CacheTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = pathlib.Path(self._tmp.name)
        self.root = base / "proj"
        self.root.mkdir()
        _write_project(self.root)
        # Output lives OUTSIDE the analyzed root so reports are not scanned.
        self.out = base / "out"
        self.cache_path = self.out / CACHE_FILENAME
        self.files = sorted(self.root.rglob("*.py"))

    def tearDown(self):
        self._tmp.cleanup()

    def _rel(self, path: pathlib.Path) -> str:
        return path.relative_to(self.root).as_posix()

    def _signature(self) -> str:
        return cache_signature(
            _VERSION,
            project_path=self.root,
            rules_config={},
            scope="all",
            include_content=False,
            project_type="generic",
        )

    def _seed(self, marker: str = "cached") -> None:
        cache = ModuleCache(self.cache_path, self._signature(), _VERSION)
        for path in self.files:
            cache.store(
                self._rel(path),
                file_content_hash(path),
                {"path": self._rel(path), "lines": 99, "marker": marker},
            )
        cache.save()

    def _loaded_cache(self) -> ModuleCache:
        cache = ModuleCache(self.cache_path, self._signature(), _VERSION)
        cache.load()
        return cache

    def _run(self, cache: ModuleCache | None):
        return run_parallel_analysis(
            self.files,
            {},
            "all",
            project_path=self.root,
            max_workers=1,
            include_content=False,
            cache=cache,
        )


class TestReuse(_CacheTestBase):
    @patch(
        "analyzer.parallel_analysis.analyze_chunk_worker",
        side_effect=AssertionError("worker pool was used for a full cache hit"),
    )
    def test_all_hits_skip_the_worker_pool(self, _mock):
        self._seed()

        results = self._run(self._loaded_cache())

        self.assertEqual(len(results), len(self.files))
        for result in results:
            self.assertEqual(result["marker"], "cached")

    def test_changed_file_is_reanalyzed(self):
        self._seed()
        (self.root / "pkg" / "b.py").write_text("def b():\n    return 3\n", encoding="utf-8")

        results = self._run(self._loaded_cache())
        by_path = {r["path"]: r for r in results}

        self.assertEqual(by_path["pkg/a.py"]["marker"], "cached")  # reused
        self.assertNotIn("marker", by_path["pkg/b.py"])  # re-analyzed
        self.assertIn("functions", by_path["pkg/b.py"])

    def test_results_are_sorted_by_path(self):
        self._seed()

        results = self._run(self._loaded_cache())
        paths = [r["path"] for r in results]

        self.assertEqual(paths, sorted(paths))

    def test_no_cache_never_reuses_nor_writes(self):
        self._seed()

        results = self._run(None)
        by_path = {r["path"]: r for r in results}

        for result in by_path.values():
            self.assertNotIn("marker", result)  # fully re-analyzed
        # cache file untouched (still the seeded one)
        data = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertEqual(data["entries"]["pkg/a.py"]["result"]["marker"], "cached")

    def test_cache_file_refreshed_after_run(self):
        self._seed()
        (self.root / "pkg" / "b.py").write_text("def b():\n    return 3\n", encoding="utf-8")

        self._run(self._loaded_cache())

        refreshed = self._loaded_cache()
        for path in self.files:
            self.assertIsNotNone(
                refreshed.lookup(self._rel(path), file_content_hash(path)),
                self._rel(path),
            )


class TestTransparency(_CacheTestBase):
    def _run_once(self):
        analyzer = ProjectAnalyzer(str(self.root), str(self.out), workers=1)
        analyzer.run()
        with open(self.out / "project_context.json", encoding="utf-8") as f:
            data = json.load(f)
        data.pop("analyzed_at", None)
        return data

    def test_second_run_output_matches_first(self):
        first = self._run_once()
        self.assertTrue(self.cache_path.exists(), "cache file should be written")

        second = self._run_once()

        self.assertEqual(first, second)

    def test_no_cache_config_writes_no_cache_file(self):
        analyzer = ProjectAnalyzer(str(self.root), str(self.out), workers=1)
        analyzer.config = dataclasses.replace(analyzer.config, cache=False)
        analyzer.run()

        self.assertFalse(self.cache_path.exists())


if __name__ == "__main__":
    unittest.main()
