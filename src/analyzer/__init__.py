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
import importlib.metadata
import pathlib
import re


def _get_version() -> str:
    """Dynamically identifies the project version.

    Prioritizes official metadata (installed package) and falls back to
    parsing pyproject.toml for development environments.
    """
    # 1. Try official metadata (Installed mode)
    try:
        return importlib.metadata.version("qgis-plugin-analyzer")
    except importlib.metadata.PackageNotFoundError:
        pass

    # 2. Fallback to pyproject.toml (Development mode)
    try:
        current_path = pathlib.Path(__file__).resolve()
        # Search up to 3 levels for pyproject.toml
        for parent in [
            current_path.parent,
            current_path.parents[1],
            current_path.parents[2],
        ]:
            pyproject = parent / "pyproject.toml"
            if pyproject.exists():
                with open(pyproject, encoding="utf-8") as f:
                    content = f.read()
                    # Match version = "X.Y.Z" under [project] or [tool.poetry]
                    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
                    if match:
                        return match.group(1)
    except Exception:
        pass

    return "unknown"


__version__ = _get_version()
