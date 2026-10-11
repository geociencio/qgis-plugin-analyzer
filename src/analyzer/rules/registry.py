"""Unified rule registry: single source of truth for rule metadata.

Consolidates the previously scattered rule identifiers (regex QGIS rules, AST
visitor rules, Bandit-inspired security checks, secret detectors and anti-pattern
rules) behind one declarative catalog (:mod:`analyzer.rules.catalog`). From here
the project derives the scope mapping (:mod:`analyzer.rules.scopes`), the
``list-rules`` command output and the generated ``RULES.md``.
"""

from __future__ import annotations

from dataclasses import dataclass

from .catalog import CATEGORY_ORDER, INFORMATIONAL_ROWS, RAW_RULES


@dataclass(frozen=True)
class Rule:
    """Metadata for a single analysis rule.

    Attributes:
        id: Stable rule identifier.
        severity: Descriptive severity (``high``, ``medium`` or ``low``).
        category: Catalog section key (see :data:`CATEGORY_ORDER`).
        description: Short human-readable description.
        recommendation: How to fix the finding.
        scopes: Analysis scopes in which the rule is enabled.
        sources: Emitters (``regex``, ``visitor``, ``security``, ``secrets``).
        emitted: Whether the rule is emitted as an issue (False for informational rows).
    """

    id: str
    severity: str
    category: str
    description: str
    recommendation: str
    scopes: tuple[str, ...]
    sources: tuple[str, ...]
    emitted: bool = True


RULE_CATALOG: dict[str, Rule] = {row[0]: Rule(*row) for row in RAW_RULES}


def get_rule(rule_id: str) -> Rule | None:
    """Return the catalog entry for ``rule_id``, or None if unknown.

    Args:
        rule_id: The rule identifier to look up.

    Returns:
        The matching :class:`Rule`, or None.
    """
    return RULE_CATALOG.get(rule_id)


def get_rules() -> list[Rule]:
    """Return the emitted rules (the projection used by ``list-rules``/``RULES.md``).

    Returns:
        The catalog entries whose ``emitted`` flag is True.
    """
    return [rule for rule in RULE_CATALOG.values() if rule.emitted]


def rules_for_scope(scope: str) -> set[str]:
    """Return the ids of the rules enabled in ``scope``.

    Args:
        scope: The analysis scope key.

    Returns:
        A set of rule ids.
    """
    return {rule.id for rule in RULE_CATALOG.values() if scope in rule.scopes}


def categories() -> list[tuple[str, str, str, str]]:
    """Return the ordered catalog sections.

    Returns:
        A list of ``(key, number, title, intro)`` tuples.
    """
    return list(CATEGORY_ORDER)


# Lightweight export for the visitors' runtime guard (keeps the import cheap:
# :mod:`analyzer.rules.catalog` has no heavy dependencies).
KNOWN_RULE_IDS: frozenset[str] = frozenset(RULE_CATALOG)

__all__ = [
    "INFORMATIONAL_ROWS",
    "KNOWN_RULE_IDS",
    "RULE_CATALOG",
    "Rule",
    "categories",
    "get_rule",
    "get_rules",
    "rules_for_scope",
]
