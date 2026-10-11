"""Regression test: the fix-handler registry is populated on import.

Importing ``analyzer.fixer`` must eagerly import the handler registrations
(``analyzer.fix_handlers``); otherwise the registry stays silently empty and no
auto-fix is ever offered (see ``AGENT_LESSONS.md`` 2026-10-10).
"""

import unittest

from analyzer.fixer import registry


class TestFixRegistryPopulated(unittest.TestCase):
    def test_builtin_handlers_registered(self):
        expected = {
            "GDAL_DIRECT_IMPORT",
            "QGIS_LEGACY_IMPORT",
            "PRINT_STATEMENT",
            "MISSING_I18N",
        }

        for issue_type in expected:
            self.assertIsNotNone(registry.get_handler(issue_type), issue_type)


if __name__ == "__main__":
    unittest.main()
