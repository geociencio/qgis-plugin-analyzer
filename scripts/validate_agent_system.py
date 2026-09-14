#!/usr/bin/env python3
"""Validate the agentic system (skills/workflows) for structural consistency.

Checks:
    1. Every ``SKILL.md`` has ``name`` + ``description`` frontmatter.
    2. Every workflow has ``description``, ``agent`` (one of the 3 ids),
       and ``skills`` frontmatter.
    3. Workflows only reference skills that exist (no phantoms).
    4. The root ``AGENTS.md`` workflow/skill tables match the files on disk
       (no omissions, no phantoms).

Exit code 0 when clean, 1 otherwise.

Usage:
    validate_agent_system.py           # full validation
    validate_agent_system.py --graph   # also print a workflow → skill graph
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".agent" / "skills"
WORKFLOWS_DIR = ROOT / ".agent" / "workflows"
AGENTS_FILE = ROOT / "AGENTS.md"

VALID_AGENTS = {"architect", "qa_engineer", "auditor"}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def _read_frontmatter(path: Path) -> dict | None:
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _skills() -> dict[str, dict]:
    found: dict[str, dict] = {}
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        meta = _read_frontmatter(path)
        name = path.parent.name
        found[name] = {"path": path, "meta": meta}
    return found


def _workflows() -> dict[str, dict]:
    found: dict[str, dict] = {}
    for path in sorted(WORKFLOWS_DIR.glob("*.md")):
        if path.name == "index.md":
            continue
        meta = _read_frontmatter(path)
        found[path.stem] = {"path": path, "meta": meta}
    return found


def _table_rows(marker: str) -> list[str]:
    """Extract body rows (excluding header/separator) between two markers."""
    text = AGENTS_FILE.read_text(encoding="utf-8")
    start = marker
    end = marker.replace("START", "END")
    if start not in text or end not in text:
        return []
    block = text.split(start, 1)[1].split(end, 1)[0]
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.fullmatch(r"[\s|\-:]+", line):
            continue
        if line.startswith("|"):
            rows.append(line.strip("|").strip())
    return rows[1:] if rows else []  # drop header row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", action="store_true", help="print workflow graph")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    skills = _skills()
    workflows = _workflows()

    # 1. Skill frontmatter
    for name, entry in skills.items():
        meta = entry["meta"]
        if meta is None:
            errors.append(f"skill '{name}': missing/invalid YAML frontmatter")
            continue
        for field in ("name", "description"):
            if not meta.get(field):
                errors.append(f"skill '{name}': missing '{field}'")

    # 2. Workflow frontmatter + agent id
    for name, entry in workflows.items():
        meta = entry["meta"]
        if meta is None:
            errors.append(f"workflow '{name}': missing/invalid YAML frontmatter")
            continue
        if not meta.get("description"):
            errors.append(f"workflow '{name}': missing 'description'")
        agent = meta.get("agent")
        if agent not in VALID_AGENTS:
            errors.append(
                f"workflow '{name}': invalid agent '{agent}' (expected {sorted(VALID_AGENTS)})"
            )
        if "skills" not in meta:
            errors.append(f"workflow '{name}': missing 'skills'")

    # 3. Phantom skills in workflows
    for name, entry in workflows.items():
        meta = entry["meta"] or {}
        for skill in meta.get("skills", []):
            if skill not in skills:
                errors.append(f"workflow '{name}': references non-existent skill '{skill}'")

    # 4. AGENTS.md table consistency
    workflow_table = _table_rows("<!-- WORKFLOWS_TABLE_START -->")
    if workflow_table:
        listed_wf = {
            row.split("|")[0].strip().strip("`").strip("/").strip()
            for row in workflow_table
            if "|" in row
        }
        for name in workflows:
            if name not in listed_wf:
                errors.append(f"AGENTS.md: workflow '/{name}' missing from workflow table")
        for name in listed_wf:
            if name not in workflows:
                errors.append(f"AGENTS.md: workflow '/{name}' listed but no file found")
    else:
        warnings.append("AGENTS.md: no WORKFLOWS_TABLE markers found (skipping table check)")

    # 5. .agent/AGENTS.md must be a pointer
    pointer = ROOT / ".agent" / "AGENTS.md"
    if "Do not edit this file" not in pointer.read_text(encoding="utf-8"):
        warnings.append(".agent/AGENTS.md is not a compatibility pointer")

    # Report
    if args.graph:
        print("workflow → skills graph:")
        for name in sorted(workflows):
            meta = workflows[name]["meta"] or {}
            print(f"  /{name} ({meta.get('agent', '?')}): {', '.join(meta.get('skills', []))}")

    print(f"skills: {len(skills)}  workflows: {len(workflows)}")
    for warning in warnings:
        print(f"  WARN: {warning}")
    for error in errors:
        print(f"  FAIL: {error}")

    if errors:
        print(f"\nvalidate_agent_system: {len(errors)} error(s)")
        return 1
    print("\nvalidate_agent_system: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
