# Antigravity Framework Quick Reference (Gen 5)

## 🏗️ Core Architecture
- **Pure Core Logic**: Decouple business logic from UI/Framework libraries.
- **3-Level Validation**: Type, Schema, and Business validation in all services.
- **Extract-then-Compute**: Pattern for reliable data processing.

## 🤖 AI Agent Roles
- **@architect**: Strategic planning and core design.
- **@qa_engineer**: Testing and stability validation.
- **@auditor**: Standards and architectural auditing.

## 🛠️ Specialized Blueprints (Scaffolds)
- **QGIS**: for QGIS plugin development.
- **Mining**: for geological and mining domain tools.
- **Use**: Copy from `scaffold/` to `.agent/` to extend capabilities.

## 🚀 Key Commands
- `uv sync`: Install dependencies.
- `python3 scripts/skill_sync.py`: Validate agent system integrity.
- `python3 scripts/mcp_server.py`: Start the MCP server for AI tools.
