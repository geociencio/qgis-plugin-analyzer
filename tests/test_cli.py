import io
import unittest
from contextlib import redirect_stdout
from analyzer.cli.app import CLIApp


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.app = CLIApp()

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
        # By default, unknown command is treated as path for 'analyze'
        # So 'non-existent-command' is analyzed as a path.
        # It should return 0 if no files found (unless strict)
        exit_code = self.app.run(["non-existent-command"])
        self.assertEqual(exit_code, 0)

    def test_legacy_default_analyze(self):
        # CLIApp._parse_args defaults to 'analyze' if first arg is a path
        f = io.StringIO()
        with redirect_stdout(f):
             exit_code = self.app.run(["/tmp"])
        
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
