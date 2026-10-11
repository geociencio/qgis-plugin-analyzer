import io
import pathlib
import tempfile
import unittest
from contextlib import redirect_stdout

from analyzer.cli.app import CLIApp


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.app = CLIApp()
        self._tmp = tempfile.TemporaryDirectory()
        self.out = pathlib.Path(self._tmp.name) / "out"

    def tearDown(self):
        self._tmp.cleanup()

    def test_version_command(self):
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = self.app.run(["version"])

        self.assertEqual(exit_code, 0)
        output = f.getvalue()
        self.assertIn("qgis-analyzer", output)

    def test_list_rules_command(self):
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = self.app.run(["list-rules"])

        self.assertEqual(exit_code, 0)
        output = f.getvalue()
        self.assertIn("UNPRECISE_LAYER", output)
        self.assertIn("UNSAFE_SUBPROCESS", output)

    def test_invalid_command(self):
        # By default, an unknown command is treated as a path for 'analyze',
        # so 'non-existent-command' is analyzed as a path. It returns 0 when no
        # files are found (unless strict). Use a temp --output so the test does
        # not dirty the repository's analysis_results/ directory.
        exit_code = self.app.run(["non-existent-command", "-o", str(self.out)])

        self.assertEqual(exit_code, 0)

    def test_legacy_default_analyze(self):
        # CLIApp._parse_args defaults to 'analyze' if first arg is a path.
        # Redirect --output to a temp dir to avoid polluting the working tree.
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = self.app.run(["/tmp", "-o", str(self.out)])

        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
