#!/usr/bin/env python3
"""Regenerate ``RULES.md`` from the unified rule catalog.

The catalog lives in ``src/analyzer/rules/catalog.py``; this adapter renders the
Markdown documentation so it can never drift from the code.

Usage:
    python scripts/generate_rules_md.py          # write RULES.md
    python scripts/generate_rules_md.py --check  # fail if RULES.md is stale
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULES_MD = PROJECT_ROOT / "RULES.md"

# Allow running via ``python scripts/generate_rules_md.py`` without installation.
_SRC = PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from analyzer.rules import render_rules_md  # noqa: E402


def main() -> int:
    """Render ``RULES.md`` (or verify it with ``--check``).

    Returns:
        0 on success, 1 when ``--check`` finds the file out of date.
    """
    rendered = render_rules_md()

    if "--check" in sys.argv:
        current = RULES_MD.read_text(encoding="utf-8") if RULES_MD.exists() else ""
        if current != rendered:
            print("❌ RULES.md is out of date. Run: python scripts/generate_rules_md.py")
            return 1
        print("✅ RULES.md is up to date.")
        return 0

    RULES_MD.write_text(rendered, encoding="utf-8")
    print(f"✅ Wrote {RULES_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
