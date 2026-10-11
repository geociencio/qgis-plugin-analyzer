"""Analysis scope → rule-id mappings, derived from the unified rule catalog.

A rule's scope is declared exactly once (on the rule, in
:mod:`analyzer.rules.catalog`); this module projects it into the
``{scope: {rule_id}}`` shape consumed by the engine's issue filtering and the
visitors' reporting gate.
"""

from __future__ import annotations

from .registry import RULE_CATALOG


def _build_scope_rules() -> dict[str, set[str]]:
    """Project ``rule.scopes`` into a ``{scope: {rule_id}}`` mapping.

    Returns:
        The scope→rule-ids map.
    """
    scope_rules: dict[str, set[str]] = {}
    for rule in RULE_CATALOG.values():
        for scope in rule.scopes:
            scope_rules.setdefault(scope, set()).add(rule.id)
    return scope_rules


SCOPE_RULES: dict[str, set[str]] = _build_scope_rules()

__all__ = ["SCOPE_RULES"]
