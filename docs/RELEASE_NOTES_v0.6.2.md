# 🚀 Release Notes v0.6.2: Precise Complexity Tracking

This release introduces granular complexity metrics to `project_context.json`, moving away from aggregated module-level scores. This allows developers to precisely track the impact of refactoring efforts like "Extract Method" on cognitive complexity.

## Key Changes

### 📊 Per-Function Complexity Metrics
The analyzer now calculates and reports Cyclomatic Complexity (CC) for each individual function.
- **Before**: `complexity` was a sum of all branches in the entire file.
- **After**: `complexity` is calculated per function using AST analysis.

### ⚠️ Automatic Complexity Warning
A new rule `HIGH_COMPLEXITY` has been added. The scanner will now emit a warning for any function with a Cyclomatic Complexity greater than **15**, helping you spot maintenance hotspots instantly.

### 🛠️ Developer Experience
- Refactored internal data models to support structured function objects.
- Cleaned up temporary test files post-verification.
