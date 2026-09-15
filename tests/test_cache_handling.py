"""Tests for stale-cache detection in the summary command."""

import datetime
import json
import os
import pathlib
import tempfile
import time
import unittest

from analyzer.commands import (
    _detect_stale_cache,
    _humanize_age,
    _parse_analyzed_at,
)


class TestCacheHandling(unittest.TestCase):
    """Unit tests for the summary stale-cache helpers."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.source = self.tmp / "mod.py"
        self.source.write_text("x = 1\n", encoding="utf-8")

    def _write_json(self, analyzed_at=None, project_path=None):
        data = {"schema_version": 1}
        if analyzed_at is not None:
            data["analyzed_at"] = analyzed_at
        if project_path is not None:
            data["project_path"] = project_path
        path = self.tmp / "project_context.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_parse_analyzed_at(self):
        self.assertIsNone(_parse_analyzed_at(None))
        self.assertIsNone(_parse_analyzed_at("not-a-date"))
        self.assertIsNotNone(_parse_analyzed_at("2026-09-14T10:00:00+00:00"))

    def test_humanize_age(self):
        now = time.time()
        self.assertEqual(_humanize_age(now - 5), "5s ago")
        self.assertEqual(_humanize_age(now - 120), "2m ago")
        self.assertEqual(_humanize_age(now - 3600), "1h ago")
        self.assertEqual(_humanize_age(now - 172800), "2d ago")

    def test_future_analyzed_at_not_stale(self):
        future = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
        path = self._write_json(analyzed_at=future.isoformat(), project_path=str(self.tmp))
        self.assertIsNone(_detect_stale_cache(path))

    def test_stale_detected_when_source_newer(self):
        past = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
        path = self._write_json(analyzed_at=past.isoformat(), project_path=str(self.tmp))
        warning = _detect_stale_cache(path)
        self.assertIsNotNone(warning)
        self.assertIn("stale", warning)
        self.assertIn("mod.py", warning)

    def test_fallback_to_mtime_when_no_analyzed_at(self):
        path = self._write_json(project_path=str(self.tmp))
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        os.utime(path, (past.timestamp(), past.timestamp()))
        os.utime(self.source, (time.time(), time.time()))
        self.assertIsNotNone(_detect_stale_cache(path))

    def test_missing_json_returns_none(self):
        self.assertIsNone(_detect_stale_cache(self.tmp / "nope.json"))


if __name__ == "__main__":
    unittest.main()
