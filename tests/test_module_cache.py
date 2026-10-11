"""Tests for the incremental module cache (hashing, signature, persistence)."""

import json
import pathlib
import tempfile
import unittest

from analyzer.module_cache import (
    CACHE_FILENAME,
    CACHE_SCHEMA,
    ModuleCache,
    analyzer_fingerprint,
    cache_signature,
    file_content_hash,
)


class TestHashing(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_content_hash_is_stable_and_change_sensitive(self):
        f = self.root / "a.py"
        f.write_text("x = 1\n", encoding="utf-8")
        first = file_content_hash(f)

        self.assertEqual(first, file_content_hash(f))
        f.write_text("x = 2\n", encoding="utf-8")
        self.assertNotEqual(first, file_content_hash(f))

    def test_analyzer_fingerprint_is_deterministic(self):
        fingerprint = analyzer_fingerprint()

        self.assertEqual(fingerprint, analyzer_fingerprint())
        self.assertEqual(len(fingerprint), 64)


class TestSignature(unittest.TestCase):
    def _sig(self, **overrides):
        base = {
            "project_path": pathlib.Path("/tmp/proj"),
            "rules_config": {},
            "scope": "all",
            "include_content": False,
            "project_type": "generic",
        }
        base.update(overrides)
        return cache_signature("1.2.3", **base)

    def test_scope_changes_signature(self):
        self.assertNotEqual(self._sig(), self._sig(scope="security"))

    def test_include_content_changes_signature(self):
        self.assertNotEqual(self._sig(), self._sig(include_content=True))

    def test_project_path_changes_signature(self):
        self.assertNotEqual(self._sig(), self._sig(project_path=pathlib.Path("/tmp/other")))

    def test_rules_change_signature(self):
        self.assertNotEqual(self._sig(), self._sig(rules_config={"x": 1}))

    def test_same_inputs_same_signature(self):
        self.assertEqual(self._sig(), self._sig())


class TestModuleCache(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.path = self.root / CACHE_FILENAME

    def tearDown(self):
        self._tmp.cleanup()

    def test_round_trip(self):
        cache = ModuleCache(self.path, "sig", "1.0")
        cache.store("a.py", "h1", {"path": "a.py", "lines": 1})
        cache.save()

        again = ModuleCache(self.path, "sig", "1.0")
        again.load()

        self.assertEqual(again.lookup("a.py", "h1"), {"path": "a.py", "lines": 1})

    def test_signature_mismatch_discards_cache(self):
        cache = ModuleCache(self.path, "sig", "1.0")
        cache.store("a.py", "h1", {"path": "a.py"})
        cache.save()

        other = ModuleCache(self.path, "different", "1.0")
        other.load()

        self.assertIsNone(other.lookup("a.py", "h1"))

    def test_hash_mismatch_is_a_miss(self):
        cache = ModuleCache(self.path, "sig", "1.0")
        cache.store("a.py", "h1", {"path": "a.py"})
        cache.save()

        again = ModuleCache(self.path, "sig", "1.0")
        again.load()

        self.assertIsNone(again.lookup("a.py", "h2"))
        self.assertEqual(again.lookup("a.py", "h1"), {"path": "a.py"})

    def test_corrupt_file_is_ignored(self):
        self.path.write_text("{not valid json", encoding="utf-8")

        cache = ModuleCache(self.path, "sig", "1.0")
        cache.load()  # must not raise

        self.assertIsNone(cache.lookup("a.py", "h1"))

    def test_malformed_entry_is_ignored(self):
        data = {"schema": CACHE_SCHEMA, "signature": "sig", "entries": {"a.py": "not-a-dict"}}
        self.path.write_text(json.dumps(data), encoding="utf-8")

        cache = ModuleCache(self.path, "sig", "1.0")
        cache.load()  # must not raise

        self.assertIsNone(cache.lookup("a.py", "h1"))

    def test_save_prunes_stale_entries(self):
        seed = ModuleCache(self.path, "sig", "1.0")
        seed.store("a.py", "h1", {"path": "a.py"})
        seed.store("gone.py", "hx", {"path": "gone.py"})
        seed.save()

        run = ModuleCache(self.path, "sig", "1.0")
        run.load()
        run.store("a.py", "h1", {"path": "a.py"})
        run.store("b.py", "h2", {"path": "b.py"})
        run.save()

        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], CACHE_SCHEMA)
        self.assertIn("a.py", data["entries"])
        self.assertIn("b.py", data["entries"])
        self.assertNotIn("gone.py", data["entries"])

    def test_reused_hits_are_retained_on_save(self):
        seed = ModuleCache(self.path, "sig", "1.0")
        seed.store("a.py", "h1", {"path": "a.py"})
        seed.save()

        run = ModuleCache(self.path, "sig", "1.0")
        run.load()
        reused = run.lookup("a.py", "h1")  # hit, not re-stored
        self.assertIsNotNone(reused)
        run.save()

        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertIn("a.py", data["entries"])

    def test_save_is_noop_when_empty(self):
        cache = ModuleCache(self.path, "sig", "1.0")
        cache.save()

        self.assertFalse(self.path.exists())


if __name__ == "__main__":
    unittest.main()
