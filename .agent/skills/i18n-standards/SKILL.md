# i18n Standards — qgis-plugin-analyzer

> Standards and best practices for internationalization in the qgis-plugin-analyzer codebase.

## When to Use
- When auditing or fixing i18n-related code in the analyzer itself
- When the analyzer's own UI strings or messages need translation support
- When extending the `I18nVisitor` with new i18n wrapper patterns

## Core Principles

### 1. The Analyzer Audits i18n — It Must Set the Standard
As a tool that audits QGIS plugins for i18n compliance, the analyzer's own code must follow the same standards it enforces. All user-facing strings in the analyzer (CLI messages, report labels, error messages) should use proper i18n wrappers.

### 2. Recognized i18n Wrappers
The `I18nVisitor` recognizes these as valid translation wrappers:
- `self.tr("...")` — standard QObject translation
- `QCoreApplication.translate("Context", "...")` — Qt API for non-QObject contexts
- `QObject.translate("Context", "...")` — equivalent to QCoreApplication

### 3. When to Use Each Wrapper

| Context | Use |
|---------|-----|
| Inside a QObject subclass method | `self.tr("text")` |
| `@staticmethod` or `@classmethod` | `QCoreApplication.translate("ClassName", "text")` |
| `super().__init__()` calls | `QCoreApplication.translate("ClassName", "text")` |
| Non-QObject classes (factories, utils) | `QCoreApplication.translate("ClassName", "text")` |

### 4. False Positive Prevention
- Strings inside `tr()` or `translate()` calls are NOT flagged
- Strings inside helper calls nested within translate() are also skipped (they're part of the translation pipeline)
- Format chains: `QCoreApplication.translate("Ctx", "Found {}").format(n)` — correctly skipped

## Heuristic Reference

The `I18nVisitor.is_translatable_string()` heuristic:
- Requires length ≥ 3 characters
- Skips paths (`/`, `\`, `:/`)
- Skips snake_case, CamelCase, UPPERCASE identifiers
- Skips technical keywords (`name`, `type`, `value`, etc.)
- Flags strings with spaces or terminal punctuation (`:.!?`)

## Testing i18n Changes

When modifying the i18n visitor:
1. Add test cases to `tests/test_i18n_wrappers.py` for wrapper recognition
2. Add test cases to `tests/test_i18n_heuristics.py` for string classification
3. Run `python -m pytest tests/test_i18n_wrappers.py tests/test_i18n_heuristics.py tests/test_i18n_standards.py -v`
4. Run self-audit: `uv run qgis-analyzer analyze .`

## Known Limitations

- The visitor matches `tr` and `translate` by function name only, not by full dotted path. A non-i18n method named `translate()` would be falsely skipped (extremely unlikely in QGIS plugin code).
- Short UI strings (`OK`, `Save`, `name`) are not flagged due to heuristic length/pattern filters.
- Docstrings and dict keys/values are excluded.
