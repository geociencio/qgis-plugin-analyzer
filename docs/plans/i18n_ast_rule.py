#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portable AST-based i18n hygiene rule (reference implementation).

This module is the generalized, project-agnostic version of SecInterp's
`scripts/verify_i18n_hygiene.py`. It is intended as the reference for the
`UNTRANSLATED_STRING` rule in qgis-plugin-analyzer (see
`docs/plans/upstreaming_qgis_analyzer.md`).

It parses Python source with the ``ast`` module and flags hardcoded string
literals that look user-facing but are not wrapped in a translation call
(``tr`` / ``translate``) and lack an inline ``# no-i18n`` exclusion.

It distinguishes between:

- Module/class/function docstrings (always excluded, including multi-line).
- Technical strings such as file extensions, CSS, HTML, color codes, format
  specifiers, geometry type keywords, and QSettings keys (excluded).
- Genuine user-facing strings that require translation (reported).

Usage:
    python i18n_ast_rule.py PATH [PATH ...] [--ignore-call SUFFIX]
        [--exact-ignore STRING] [--json]

Exit codes:
    0  All user-facing strings are properly handled.
    1  One or more untranslated user-facing strings were found.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

# Calls whose string arguments are safe to ignore (translations, logging, etc.).
DEFAULT_SAFE_CALL_SUFFIXES: set[str] = {
    # Translation wrappers — already translated
    "tr",
    "translate",
    # Logging — not user-facing
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    "log",
    # QGIS / Qt internals
    "connect",
    "disconnect",
    "mapLayerByName",
    "setValue",
    "setObjectName",
    "setProperty",
    "setToolTip",
    "setWhatsThis",
    "setPlaceholderText",
    "setAttribute",
    "setStyleSheet",
    "addItem",
    "insertItem",
    "findText",
    # Exception constructors — developer-facing
    "ValueError",
    "RuntimeError",
    "TypeError",
    "AttributeError",
    "KeyError",
    "NotImplementedError",
    "OSError",
    "IOError",
    "Exception",
    # Regular expression / path operations
    "compile",
    "match",
    "search",
    "sub",
    "split",
    "join",
    "format",
    "encode",
    "decode",
    "open",
    "makedirs",
    "startswith",
    "endswith",
    "with_suffix",
    "parent",
}

# Regex patterns for strings that are always technical (not user-facing).
DEFAULT_TECHNICAL_PATTERNS: list[re.Pattern[str]] = [
    # Python format specifiers
    re.compile(r"^[{.+<>^-]?\d*[dfsfeExXgGoO%nbDBcdnrsa]$"),  # e.g. '.2f', '+.2f'
    # File extensions
    re.compile(r"^\.[a-z]{2,4}$"),  # e.g. '.png', '.jpg', '.svg', '.shp'
    # MIME-style filter strings
    re.compile(r"\*\.\w+"),  # e.g. '*.png'
    # CSS / Qt stylesheet fragments
    re.compile(
        r"(background-color|border|font-weight|color:|margin|padding|QPush|QDialog|QLabel|QCombo)"
    ),
    # QGIS memory layer URI / field specs
    re.compile(r"field=\w+:\w+"),
    # Color codes (R,G,B or R,G,B,A)
    re.compile(r"^\d{1,3},\d{1,3},\d{1,3}(,\d{1,3})?$"),
    # SVG icon names
    re.compile(r"^m[A-Z][a-zA-Z]+\.svg$"),
    # Pure HTML tags (e.g. '<b>', '</b>', '<br>')
    re.compile(r"^</?[a-zA-Z][a-zA-Z0-9]*\s*/?>$"),
    # HTML attribute or fragment (contains '<' or '>' and no full readable word phrase)
    re.compile(r"^[^a-zA-Z]*<[^>]*>[^a-zA-Z]*$"),
    # Strings that are mostly HTML/special chars with minimal alpha
    re.compile(r"^[\s\|:;.,!?<>\-=\"'/\\{}()]+[a-zA-Z]{0,3}[\s\|:;.,!?<>\-=\"'/\\{}()]*$"),
    # Hex color codes
    re.compile(r"^#[0-9a-fA-F]{3,8}$"),
    # Geometry type keywords
    re.compile(r"^(Point|LineString|Polygon|MultiPoint|MultiLineString|MultiPolygon)$"),
    # Single-word QGIS layer types or geometry keywords
    re.compile(r"^(EPSG|WKT|CRS|SHP|CSV|GeoJSON|GPKG|GeoTIFF)$", re.IGNORECASE),
    # Format specifiers or pure punctuation/symbols
    re.compile(r"^[^a-zA-Z]*$"),
    # Log-level strings
    re.compile(r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    # QSettings keys (contain '/' or are camelCase)
    re.compile(r"^[a-zA-Z]+/[a-zA-Z/_]+$"),  # e.g. 'MyApp/last_dir'
    # Default filename values (just a filename, no spaces)
    re.compile(r"^\w[\w.-]*\.(png|jpg|jpeg|pdf|svg|shp|csv|json|html|txt|xml|qml)$"),
    # Pure numbers (including floats)
    re.compile(r"^-?\d+(\.\d+)?$"),
    # HTML attribute opening fragments (e.g. "<a href='", '<span style="')
    re.compile(r"^<[a-zA-Z]+\s+[a-zA-Z-]+=[\"']"),
]

# Exact strings that are always safe to ignore.
DEFAULT_SAFE_EXACT_STRINGS: set[str] = {
    "utf-8",
    "r",
    "w",
    "rb",
    "wb",
    "a",
    "en",
    "es",
}


def collect_docstring_lines(tree: ast.AST) -> set[int]:
    """Collect line numbers of all docstrings (module, class, function) via AST.

    Docstrings are the first string expression in a module, class body, or
    function body, possibly preceded by import statements (e.g. future imports).

    Args:
        tree: Parsed AST of the Python source file.

    Returns:
        Set of line numbers that belong to docstrings.
    """
    docstring_lines: set[int] = set()

    def _find_first_str_expr(body: list[ast.stmt]) -> ast.Constant | None:
        """Return the first string Constant Expr, skipping leading imports."""
        for stmt in body:
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                continue
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            ):
                return stmt.value
            break
        return None

    for node in ast.walk(tree):
        docstring_node: ast.Constant | None = None

        if isinstance(node, ast.Module):
            docstring_node = _find_first_str_expr(node.body)
        elif isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef, ast.FunctionDef)):
            docstring_node = _find_first_str_expr(node.body)

        if docstring_node is not None:
            for lineno in range(
                docstring_node.lineno,
                (docstring_node.end_lineno or docstring_node.lineno) + 1,
            ):
                docstring_lines.add(lineno)

    return docstring_lines


def is_technical_string(val: str, patterns: list[re.Pattern[str]]) -> bool:
    """Return True if the string value is clearly technical/non-translatable.

    Args:
        val: String value to inspect.
        patterns: Regex patterns identifying technical strings.

    Returns:
        True if the string should be ignored as technical.
    """
    stripped = val.strip()

    for pattern in patterns:
        if pattern.search(stripped):
            return True

    return False


class I18nAstVisitor(ast.NodeVisitor):
    """AST Visitor to detect untranslated user-facing strings."""

    def __init__(
        self,
        filepath: Path,
        lines: list[str],
        docstring_lines: set[int],
        safe_call_suffixes: set[str],
        technical_patterns: list[re.Pattern[str]],
        safe_exact_strings: set[str],
    ) -> None:
        """Initialize the visitor.

        Args:
            filepath: Path of the file being analyzed.
            lines: Source lines of the file.
            docstring_lines: Line numbers that belong to docstrings.
            safe_call_suffixes: Call suffixes whose string args are safe.
            technical_patterns: Regex patterns identifying technical strings.
            safe_exact_strings: Exact string values always safe to ignore.
        """
        self.filepath = filepath
        self.lines = lines
        self.docstring_lines = docstring_lines
        self.safe_call_suffixes = safe_call_suffixes
        self.technical_patterns = technical_patterns
        self.safe_exact_strings = safe_exact_strings
        self.violations: list[tuple[int, str, str]] = []
        self._current_call_stack: list[str] = []

    def _get_call_name(self, node: ast.expr) -> str:
        """Resolve the qualified name of a function call node.

        Args:
            node: Call function expression.

        Returns:
            Dotted name (e.g. ``self.tr`` -> ``self.tr``), or empty string.
        """
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self._get_call_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """Track the current call stack to detect safe wrappers."""
        call_name = self._get_call_name(node.func)
        self._current_call_stack.append(call_name)
        self.generic_visit(node)
        self._current_call_stack.pop()

    def visit_Constant(self, node: ast.Constant) -> None:
        """Inspect string constants for i18n hygiene violations."""
        if not isinstance(node.value, str):
            return

        val = node.value.strip()

        # 1. Empty, very short, or numeric-only strings
        if len(val) <= 1 or val.replace(".", "").replace("-", "").isdigit():
            return

        # 2. This line belongs to a docstring
        if node.lineno in self.docstring_lines:
            return

        # 3. Exact safe strings
        if val in self.safe_exact_strings:
            return

        # 4. Technical/non-translatable pattern match
        if is_technical_string(val, self.technical_patterns):
            return

        # 5. String must look user-facing: contain at least one space or real word
        has_spaces = " " in val
        has_alpha = any(c.isalpha() for c in val)
        if not (has_spaces and has_alpha):
            return

        # 6. Check if the string is inside a safe call wrapper
        for active_call in reversed(self._current_call_stack):
            if any(active_call.endswith(suffix) for suffix in self.safe_call_suffixes):
                return

        # 7. Check for inline exclusion comments on the source line
        line_num = node.lineno
        if 1 <= line_num <= len(self.lines):
            line_content = self.lines[line_num - 1]
            if "# no-i18n" in line_content or "# noqa" in line_content:
                return
            self.violations.append((line_num, val, line_content.strip()))


def verify_file(
    filepath: Path,
    safe_call_suffixes: set[str],
    technical_patterns: list[re.Pattern[str]],
    safe_exact_strings: set[str],
) -> list[tuple[int, str, str]]:
    """Analyze a single Python file for i18n hygiene violations.

    Args:
        filepath: Path to the Python file to analyze.
        safe_call_suffixes: Call suffixes whose string args are safe.
        technical_patterns: Regex patterns identifying technical strings.
        safe_exact_strings: Exact string values always safe to ignore.

    Returns:
        List of ``(line_number, string_value, source_line)`` tuples for violations.
    """
    try:
        source = filepath.read_text(encoding="utf-8")
        lines = source.splitlines()
    except OSError as e:
        print(f"⚠️  Error reading {filepath}: {e}")
        return []

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        print(f"⚠️  Syntax Error in {filepath}: {e}")
        return []

    docstring_lines = collect_docstring_lines(tree)
    visitor = I18nAstVisitor(
        filepath,
        lines,
        docstring_lines,
        safe_call_suffixes,
        technical_patterns,
        safe_exact_strings,
    )
    visitor.visit(tree)
    return visitor.violations


def _collect_files(paths: list[str]) -> list[Path]:
    """Expand the given paths into a list of Python files to scan.

    Args:
        paths: List of file or directory paths.

    Returns:
        Sorted list of ``.py`` files.
    """
    files: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            print(f"⚠️  Path not found, skipping: {path}")
            continue
        if path.is_file():
            files.append(path)
        else:
            files.extend(sorted(path.rglob("*.py")))
    return files


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Portable AST-based i18n hygiene validator.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to scan (default: current directory).",
    )
    parser.add_argument(
        "--ignore-call",
        action="append",
        default=[],
        help="Additional call suffix to treat as safe (repeatable).",
    )
    parser.add_argument(
        "--exact-ignore",
        action="append",
        default=[],
        help="Additional exact string to ignore (repeatable).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Scan the designated paths and return a validation exit code.

    Args:
        argv: Command-line arguments (defaults to ``sys.argv[1:]``).

    Returns:
        0 if no violations, 1 otherwise.
    """
    args = _build_parser().parse_args(argv)

    safe_call_suffixes = set(DEFAULT_SAFE_CALL_SUFFIXES) | set(args.ignore_call)
    safe_exact_strings = set(DEFAULT_SAFE_EXACT_STRINGS) | set(args.exact_ignore)

    files = _collect_files(args.paths)
    total_violations = 0
    report: list[dict] = []

    for file_path in files:
        violations = verify_file(
            file_path,
            safe_call_suffixes,
            DEFAULT_TECHNICAL_PATTERNS,
            safe_exact_strings,
        )
        if violations:
            total_violations += len(violations)
            if not args.json:
                print(f"🚨 Violations in {file_path}:")
                for line, val, content in violations:
                    display_val = val[:80] + "…" if len(val) > 80 else val
                    print(f'   Line {line:4d} | "{display_val}"')
                    print(f"            Code: {content[:120]}")
                print()
            for line, val, _ in violations:
                report.append({"path": str(file_path), "line": line, "string": val})

    if args.json:
        print(json.dumps({"violations": report, "count": total_violations}, indent=2))

    if total_violations > 0:
        if not args.json:
            print(f"❌ Failed: {total_violations} untranslated user-facing string(s) found.")
            print("💡 Fix: Wrap in tr(...) or add '# no-i18n' to skip.")
        return 1

    if not args.json:
        print(f"✅ Success: all user-facing strings are properly handled ({len(files)} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
