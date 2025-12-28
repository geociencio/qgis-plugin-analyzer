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

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pathlib

@dataclass
class ModuleAnalysis:
    """Analysis of a Python module."""
    path: str
    lines: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    complexity: int
    docstrings: Dict[str, Any]
    has_main: bool
    file_size_kb: float
    syntax_error: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProjectContext:
    """Full project context."""
    project_name: str
    structure: Dict[str, Any] = field(default_factory=dict)
    entry_points: List[str] = field(default_factory=list)
    tech_stack: Dict[str, List[str]] = field(default_factory=dict)
    patterns: Dict[str, Any] = field(default_factory=dict)
    technical_debt: List[Dict[str, Any]] = field(default_factory=list)
    optimization_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    security_issues: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
