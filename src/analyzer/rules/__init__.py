"""Rules package for the QGIS Plugin Analyzer.

Exposes the unified rule catalog (:mod:`analyzer.rules.registry`), its renderers
(:mod:`analyzer.rules.render`) and the legacy regex rule accessor.
"""

from .qgis_rules import I18N_METHODS, get_qgis_audit_rules
from .registry import (
    KNOWN_RULE_IDS,
    RULE_CATALOG,
    Rule,
    categories,
    get_rule,
    get_rules,
    rules_for_scope,
)
from .render import render_list_rules_text, render_rules_md

__all__ = [
    "I18N_METHODS",
    "KNOWN_RULE_IDS",
    "RULE_CATALOG",
    "Rule",
    "categories",
    "get_qgis_audit_rules",
    "get_rule",
    "get_rules",
    "render_list_rules_text",
    "render_rules_md",
    "rules_for_scope",
]
