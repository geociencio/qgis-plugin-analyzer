"""Renderers for the rule catalog (``RULES.md`` and ``list-rules`` text)."""

from __future__ import annotations

from .catalog import CATEGORY_ORDER, INFORMATIONAL_ROWS
from .registry import RULE_CATALOG, Rule, get_rules

_SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
_SEVERITY_LABEL = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}

_HEADER = """# Rule Catalog: QGIS Plugin Analyzer 📜

> **Generated** by `scripts/generate_rules_md.py` from
> `src/analyzer/rules/catalog.py` — do not edit by hand.

This document details the audit rules implemented in the analyzer to ensure that
plugins follow official QGIS standards and development best practices.

All rules support inline suppression via `# noqa` (suppress everything on the
line) or `# noqa: RULE_ID` (suppress a single rule).
"""

_TABLE_HEADER = (
    "| Rule ID | Severity | Description | Recommendation |\n| :--- | :--- | :--- | :--- |"
)


def _sort_key(rule: Rule) -> tuple[int, str]:
    return (_SEVERITY_RANK.get(rule.severity, 99), rule.id)


def _rule_row(rule: Rule) -> str:
    if rule.emitted:
        rule_id = f"`{rule.id}`"
        severity = _SEVERITY_LABEL.get(rule.severity, rule.severity)
    else:
        rule_id = f"~~`{rule.id}`~~"
        severity = "—"
    return f"| {rule_id} | {severity} | {rule.description} | {rule.recommendation} |"


def render_rules_md() -> str:
    """Render the full ``RULES.md`` document from the catalog.

    Returns:
        The Markdown document as a string (newline-terminated, deterministic).
    """
    by_category: dict[str, list[Rule]] = {key: [] for key, _, _, _ in CATEGORY_ORDER}
    for rule in get_rules():
        by_category.setdefault(rule.category, []).append(rule)
    # Non-emitted rows (e.g. the struck-through SIGNAL_LEAK) still belong to a section.
    for rule in RULE_CATALOG.values():
        if not rule.emitted:
            by_category.setdefault(rule.category, []).append(rule)

    parts: list[str] = [_HEADER]
    for key, number, title, intro in CATEGORY_ORDER:
        rules = sorted(by_category.get(key, []), key=_sort_key)
        if not rules and not intro:
            continue
        parts.append(f"## {number}. {title}\n")
        if intro:
            parts.append(f"{intro}\n")
        parts.append(_TABLE_HEADER)
        parts.extend(_rule_row(rule) for rule in rules)
        parts.append("")

    parts.append("### Informational (not issues)\n")
    parts.append("| Name | Description |\n| :--- | :--- |")
    parts.extend(f"| {name} | {description} |" for name, description in INFORMATIONAL_ROWS)
    parts.append("")

    return "\n".join(parts) + "\n"


def render_list_rules_text() -> str:
    """Render the ``list-rules`` human-readable catalog.

    Returns:
        A newline-terminated, category-grouped listing of every emitted rule.
    """
    rules = get_rules()
    lines = [f"📋 QGIS Plugin Analyzer — Rule Catalog ({len(rules)} rules)", "=" * 52]
    for key, _number, title, _intro in CATEGORY_ORDER:
        section = sorted((r for r in rules if r.category == key), key=_sort_key)
        if not section:
            continue
        lines.append(f"\n{title}")
        for rule in section:
            lines.append(f"- [{rule.severity.upper()}] {rule.id}: {rule.description}")
    lines.append("")
    return "\n".join(lines)
