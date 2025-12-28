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
from .engine import ProjectAnalyzer

def main():
    parser = argparse.ArgumentParser(description="QGIS Plugin Analyzer - Un guardián para tu código PyQGIS")
    parser.add_argument("project_path", help="Ruta al proyecto de QGIS a analizar")
    parser.add_argument("-o", "--output", help="Directorio de salida para los reportes", default="./analysis_results")
    
    args = parser.parse_args()
    
    try:
        analyzer = ProjectAnalyzer(args.project_path, args.output)
        analyzer.run()
    except KeyboardInterrupt:
        print("\n⏹️ Análisis interrumpido.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
