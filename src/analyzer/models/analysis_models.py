"""Core data models for project and module analysis."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ModuleAnalysis:
    """Analysis results for a single Python module.

    Attributes:
        path: Relative path to the file.
        lines: Total number of lines.
        functions: List of function metadata dictionaries.
        classes: List of class signatures.
        imports: List of imported modules.
        complexity: Cyclomatic complexity score.
        docstrings: Dictionary containing docstring presence information.
        has_main: True if the module has a __main__ guard.
        file_size_kb: Size of the file in kilobytes.
        syntax_error: True if the file has syntax errors.
        metadata: Additional analysis metadata.
    """

    path: str
    lines: int
    functions: List[Dict[str, Any]]
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
    """Consolidated context for an entire project analysis.

    Attributes:
        project_name: Name of the project under analysis.
        structure: Dictionary describing project file structure.
        entry_points: List of detected entry points.
        tech_stack: Dictionary of detected technologies and their versions.
        patterns: Dictionary of detected architectural patterns.
        technical_debt: List of identified technical debt items.
        optimization_opportunities: List of suggested optimizations.
        security_issues: List of identified security vulnerabilities.
        metrics: Consolidated project-level metrics and scores.
    """

    project_name: str
    structure: Dict[str, Any] = field(default_factory=dict)
    entry_points: List[str] = field(default_factory=list)
    tech_stack: Dict[str, List[str]] = field(default_factory=dict)
    patterns: Dict[str, Any] = field(default_factory=dict)
    technical_debt: List[Dict[str, Any]] = field(default_factory=list)
    optimization_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    security_issues: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
