import json
import os

try:
    path = "analysis_results/project_context.json"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        exit(1)

    with open(path) as f:
        data = json.load(f)

    # Scores are under metrics
    metrics = data.get("metrics", {})
    mod_score = metrics.get("quality_score", "N/A")
    maint_score = metrics.get("maintainability_score", "N/A")
    print(f"Module Stability Score: {mod_score}/100")
    print(f"Code Maintainability Score: {maint_score}/100")

    issues = []
    for module in data.get("modules", []):
        for issue in module.get("ast_issues", []):
            issue["file"] = module.get("path")
            issues.append(issue)

    # Count by type
    counts = {}
    for i in issues:
        t = i.get("type", "unknown")
        counts[t] = counts.get(t, 0) + 1

    print("\nIssue Counts:")
    if not counts:
        print("✅ No issues detected!")
    else:
        for t, c in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{t}: {c}")

    print("\nSample Issues (first 10):")
    for i in issues[:10]:
        print(f"[{i['type']}] in {i['file']}:{i.get('line', '?')} - {i['message']}")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
