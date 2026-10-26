"""End-to-end JSON contract tests for the analyze/security commands."""

import contextlib
import io
import json
import pathlib
import tempfile
import unittest

from analyzer.cli import CLIApp


class TestCliJsonOutput(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        (self.root / "metadata.txt").write_text(
            "[general]\nname=Demo\nversion=1.0\nemail=a@b.c\n", encoding="utf-8"
        )
        (self.root / "plugin.py").write_text(
            'def run(cmd):\n    eval("1+1")\n    return cmd\n', encoding="utf-8"
        )
        self.out = self.root / "out"

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, argv: list[str]) -> tuple[str, str, int | None]:
        stdout, stderr = io.StringIO(), io.StringIO()
        code: int | None = 0
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = CLIApp().run(argv)
            except SystemExit as exc:
                code = int(exc.code) if isinstance(exc.code, int) else 1
        return stdout.getvalue(), stderr.getvalue(), code

    def test_analyze_json_stdout_is_machine_readable(self):
        stdout, _stderr, code = self._run(
            ["analyze", str(self.root), "-o", str(self.out), "--json"]
        )

        self.assertEqual(code, 0)
        data = json.loads(stdout)
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["schema"], 1)
        self.assertIn("modules", data)

    def test_security_json_blocks_on_high_finding(self):
        stdout, _stderr, code = self._run(
            ["security", str(self.root), "-o", str(self.out), "--json"]
        )

        self.assertEqual(code, 1)
        data = json.loads(stdout)
        self.assertEqual(data["command"], "security")
        self.assertEqual(data["scope"], "security")
        self.assertEqual(data["schema"], 1)
        self.assertEqual(data["schema_version"], 1)
        self.assertGreaterEqual(data["summary"]["critical"], 1)
        self.assertTrue(any(item["rule_id"] == "B307" for item in data["findings"]))


if __name__ == "__main__":
    unittest.main()
