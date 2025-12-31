# /***************************************************************************
#  QGIS Plugin Analyzer
#                                  A QGIS tool
#  Static code analysis and standards audit for QGIS plugins.
#                               -------------------
#         begin                : 2025-12-28
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/


import argparse
import pathlib
import sys

from .engine import ProjectAnalyzer
from .utils import logger, setup_logger


def main():
    parser = argparse.ArgumentParser(
        description="QGIS Plugin Analyzer - A guardian for your PyQGIS code"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Analyze Command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze an existing QGIS plugin")
    analyze_parser.add_argument("project_path", help="Path to the QGIS project to analyze")
    analyze_parser.add_argument(
        "-o", "--output", help="Output directory for reports", default="./analysis_results"
    )
    analyze_parser.add_argument(
        "-p", "--profile", help="Configuration profile from pyproject.toml", default="default"
    )

    # Legacy support / default to analyze if no command provided
    if len(sys.argv) > 1 and sys.argv[1] not in ["analyze", "-h", "--help"]:
        # If the first argument is a path (doesn't start with -), assume 'analyze'
        if not sys.argv[1].startswith("-"):
            sys.argv.insert(1, "analyze")

    args = parser.parse_args()

    # Initialize logger (default to analysis_results if not specified)
    output_dir = pathlib.Path(getattr(args, "output", "./analysis_results")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_logger(output_dir)

    try:
        
        if args.command == "analyze":
            analyzer = ProjectAnalyzer(args.project_path, args.output, args.profile)
            success = analyzer.run()
            if not success:
                sys.exit(1)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        logger.info("\n⏹️ Analysis interrupted.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Critical Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
