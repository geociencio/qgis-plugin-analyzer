# PROJECT SUMMARY - qgis_plugin_analyzer
Analysis Date: 2026-02-01 17:08:01
Analyzer Version: 2.0 (Ai-Context-Core)

## 📊 KEY METRICS
- **Total Modules**: 35
- **Lines of Code**: 8,798
- **Total Size**: 18.8 MB
- **Average Complexity**: 31.1
- **Avg Maintenance Index**: 39.7
- **Docstring Coverage**: 86.1%
- **Quality Score**: 71.0/100
- **Test Files**: 10

## 📁 STRUCTURE
- **Python Files**: 45
- **Total Files**: 1679
- **Primary File Types**: .json, .md, .py, .sample, .yaml

## 🚨 CRITICAL ISSUES
### 🔒 Security Issues:
- **.ai-context/analyze_project_optfixed.py**: 27 issues (Max: HIGH)
- **antigravity-framerepo/scaffold/skills/data-science/scripts/validate_dataset.py**: 1 issues (Max: LOW)
- **antigravity-framerepo/bootstrap.py**: 2 issues (Max: LOW)

### 🏗️ Critical Technical Debt:
- **src/analyzer/engine.py**: 3 issues (Score: 6)
- **.ai-context/ai_workflow.py**: 2 issues (Score: 6)
- **src/analyzer/scanner.py**: 3 issues (Score: 6)
- **.ai-context/analyze_project_optfixed.py**: 2 issues (Score: 6)
- **antigravity-framerepo/scripts/skill_sync.py**: 2 issues (Score: 4)

## 💡 MAIN RECOMMENDATIONS
### .ai-context/context_manager.py
- Consider breaking down large logic
### src/analyzer/cli.py
- Consider breaking down large logic
### src/analyzer/fixer.py
- Consider breaking down large logic

## 🏗️ DESIGN PATTERNS
### Factory
- **AIContextManager** in `.ai-context/context_manager.py` (70%)

## 🔄 GIT ANALYSIS
### Code Churn (last 30 days)
- **Files Changed**: 193
- **Additions**: +18123
- **Deletions**: -2792
- **Total Churn**: 20915

### 🔥 Hotspots
- `src/analyzer/engine.py`: 19 commits
- `src/analyzer/scanner.py`: 17 commits
- `src/analyzer/cli.py`: 15 commits
- `src/analyzer/utils.py`: 14 commits
- `src/analyzer/reporters.py`: 10 commits

## 📈 COMPLEXITY DISTRIBUTION
- low (0-5): 15 modules (42.9%)
- medium (6-15): 1 modules (2.9%)
- high (16-30): 10 modules (28.6%)
- very_high (31+): 9 modules (25.7%)
