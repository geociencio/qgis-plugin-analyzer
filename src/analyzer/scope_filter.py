"""Scope-based issue filtering for the analysis pipeline.

Extracted from :mod:`analyzer.engine` to keep the orchestrator within the
project's module-size limit.
"""

from .rules.scopes import SCOPE_RULES
from .scanner import ModuleAnalysisResult


def filter_issues_by_scope(
    modules_data: list[ModuleAnalysisResult], scope: str
) -> list[ModuleAnalysisResult]:
    """Filters issues in modules based on the analysis scope.

    Args:
        modules_data: List of module analysis results.
        scope: The analysis scope.

    Returns:
        Filtered list of module analysis results.
    """
    if scope == "all":
        return modules_data

    allowed_rules = SCOPE_RULES.get(scope, set())
    if not allowed_rules:
        return modules_data

    # Filter issues in each module
    filtered_modules = []
    for module in modules_data:
        filtered_module = module.copy()
        filtered_module["ast_issues"] = [
            issue for issue in module.get("ast_issues", []) if issue.get("type") in allowed_rules
        ]
        filtered_module["security_issues"] = [
            issue
            for issue in module.get("security_issues", [])
            if issue.get("type") in allowed_rules
        ]
        filtered_modules.append(filtered_module)

    return filtered_modules
