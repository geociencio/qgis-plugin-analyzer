"""Entry builder shared by the rule catalog data modules."""

from __future__ import annotations

RuleTuple = tuple[str, str, str, str, str, tuple[str, ...], tuple[str, ...], bool]


def rule(
    rule_id: str,
    severity: str,
    category: str,
    description: str,
    recommendation: str,
    scopes: tuple[str, ...] = (),
    sources: tuple[str, ...] = ("visitor",),
    emitted: bool = True,
) -> RuleTuple:
    """Build a catalog entry tuple (id, severity, category, description, ...).

    Returns:
        The 8-field entry tuple consumed by
        :data:`analyzer.rules.catalog.RAW_RULES`.
    """
    return (rule_id, severity, category, description, recommendation, scopes, sources, emitted)
