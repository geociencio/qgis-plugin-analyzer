# v1.1.0: The Security & Licensing Release 🛡️

This version introduces advanced security auditing and official GPL v3 licensing.

### 🚀 What's New?

- **🔒 Advanced Security Auditing**: New rules to detect `UNSAFE_SUBPROCESS` (command injection risk) and `BLOCKING_NETWORK_CALL` (UI freezing risk).
- **⚖️ GPL v3 License**: Official adoption of the GNU General Public License v3.
- **🧪 Robust Testing**: New unit tests specifically for detecting vulnerabilities.
- **📊 Updated Quality Metrics**: Improved scoring precision for secure coding practices.

### 🛠️ Technical Changes
- Enhanced `QGISASTVisitor` with deep call-tree analysis for network functions.
- Renamed and reordered rules in `RULES.md` for clearer categorization.
- Version bump to `1.1.0`.

**Full Changelog**: [v1.0.0...v1.1.0](https://github.com/geociencio/qgis-plugin-analyzer/compare/v1.0.0...v1.1.0)
