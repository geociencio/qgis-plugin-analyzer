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
import sys
import pathlib
from .engine import ProjectAnalyzer
from .generator import ProjectGenerator

def main():
    parser = argparse.ArgumentParser(description="QGIS Plugin Analyzer - A guardian for your PyQGIS code")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Analyze Command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze an existing QGIS plugin")
    analyze_parser.add_argument("project_path", help="Path to the QGIS project to analyze")
    analyze_parser.add_argument("-o", "--output", help="Output directory for reports", default="./analysis_results")
    analyze_parser.add_argument("-p", "--profile", help="Configuration profile from pyproject.toml", default="default")

    # Init Command
    init_parser = subparsers.add_parser("init", help="Initialize a new QGIS plugin project")
    init_parser.add_argument("path", help="Path where the plugin will be created")
    init_parser.add_argument("-t", "--type", choices=["processing", "gui", "map_tool"], 
                            default="gui", help="Type of plugin template")
    init_parser.add_argument("--name", help="Human readable name", default="My QGIS Plugin")
    init_parser.add_argument("--author", help="Author name", default="QGIS Developer")
    init_parser.add_argument("--email", help="Author email", default="dev@qgis.org")

    # Legacy support / default to analyze if no command provided
    if len(sys.argv) > 1 and sys.argv[1] not in ["analyze", "init", "-h", "--help"]:
        # If the first argument is a path (doesn't start with -), assume 'analyze'
        if not sys.argv[1].startswith("-"):
            sys.argv.insert(1, "analyze")

    args = parser.parse_args()
    
    try:
        if args.command == "init":
            class_name = args.name.replace(" ", "").replace("-", "").capitalize()
            name_id = args.name.lower().replace(" ", "_").replace("-", "_")
            
            context = {
                "name": args.name,
                "name_id": name_id,
                "class_name": class_name,
                "description": f"A professional {args.type} plugin for QGIS.",
                "author": args.author,
                "email": args.email
            }
            
            generator = ProjectGenerator(args.path)
            generator.generate(args.type, context)
            
        elif args.command == "analyze":
            analyzer = ProjectAnalyzer(args.project_path, args.output, args.profile)
            success = analyzer.run()
            if not success:
                sys.exit(1)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⏹️ Analysis interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
