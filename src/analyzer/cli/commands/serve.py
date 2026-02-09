"""Serve command implementation for report viewing."""

import argparse
import http.server
import pathlib
import socketserver
import threading
import webbrowser

from ..base import BaseCommand


class ServeCommand(BaseCommand):
    """Command to serve and open the generated HTML report locally."""

    @property
    def name(self) -> str:
        """Command name."""
        return "serve"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Serve and open the HTML report locally"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure serve command arguments.

        Args:
            parser: The argument parser for this command.
        """
        parser.add_argument(
            "-o",
            "--output",
            help="Path to the analysis results directory",
            default="./analysis_results",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8000,
            help="Port to serve on (default: 8000)",
        )
        parser.add_argument(
            "--no-browser",
            action="store_true",
            help="Do not open the browser automatically",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the serve command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success).
        """
        output_dir = pathlib.Path(args.output).resolve()
        report_file = output_dir / "PROJECT_SUMMARY.html"

        if not report_file.exists():
            print(f"❌ Report not found: {report_file}")
            print("Run 'qgis-analyzer analyze' first to generate a report.")
            return 1

        port = args.port
        handler = http.server.SimpleHTTPRequestHandler

        # Change directory to output_dir to serve files correctly
        import os

        os.chdir(output_dir)

        try:
            with socketserver.TCPServer(("", port), handler) as httpd:
                url = f"http://localhost:{port}/PROJECT_SUMMARY.html"
                print(f"🚀 Serving reports at: {url}")
                print("Press Ctrl+C to stop.")

                if not args.no_browser:
                    # Open browser in a separate thread to allow server to start
                    threading.Timer(1, lambda: webbrowser.open(url)).start()

                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n⏹️  Server stopped.")
            return 0
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return 1
        return 0
