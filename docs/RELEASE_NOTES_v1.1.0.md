# Release Notes - v1.1.0 🛡️

## "The Security & Licensing Release"

This release marks a significant milestone in the maturity of the QGIS Plugin Analyzer, focusing on legal clarity and proactive security auditing.

### Key Highlights

#### 🔒 Security & Safety Audit Suite
We've introduced a specialized audit layer to identify high-risk coding patterns that could compromise plugin security or stability:
- **`UNSAFE_SUBPROCESS`**: Flags dangerous command executions that bypass shell quoting or use `shell=True`, preventing potential command injection vulnerabilities.
- **`BLOCKING_NETWORK_CALL`**: Identifies synchronous network requests made within UI-related files. These calls are a common cause of "QGIS freezing" and should be offloaded to `QgsTask` or `QNetworkAccessManager`.

#### ⚖️ Official GPL v3 Adoption
To align with the QGIS ecosystem and ensure long-term community freedom, the QGIS Plugin Analyzer is now officially licensed under the **GNU General Public License v3**.

### Full Changelog

- **Added**: `UNSAFE_SUBPROCESS` rule for command injection prevention.
- **Added**: `BLOCKING_NETWORK_CALL` rule for UI responsiveness auditing.
- **Added**: Official `LICENSE` file (GPL v3).
- **Improved**: Renumbered and reorganized the `RULES.md` catalog for better readability.
- **Fixed**: Corrected rule message strings and added specialized vulnerability unit tests.

---
*Empowering the QGIS community with safer and better code.*
