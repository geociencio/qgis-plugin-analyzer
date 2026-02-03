"""CLI package for QGIS Plugin Analyzer."""

import sys

from .app import CLIApp


def main() -> None:
    """Main entry point for the QGIS Plugin Analyzer CLI."""
    app = CLIApp()
    sys.exit(app.run())


__all__ = ["CLIApp", "main"]
