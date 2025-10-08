# compare_candidates.py
"""
Compare initial_candidates.json and after_candidates.json and write a unified diff to:
  reports/compare_initial_after.md
"""
import json
import difflib
import os

REPORTS_DIR = "reports"
INITIAL = os.path.join(REPORTS_DIR, "initial_candidates.json")
AFTER = os.path.join(REPORTS_DIR, "after_candidates.json")
OUT = os.path.join(REPORTS_DIR, "compare_initial_after.md")

def read_json_lines(path):
    if not os.path.exists(path):
        return None
    data = json.load(open(path, "r", encoding="utf8"))
    return json.dumps(data, indent=2, ensure_ascii=False).splitlines()

def main():
    a = read_json_lines(INITIAL)
    b = read_json_lines(AFTER)
    if a is None or b is None:
        print("Missing file(s). Make sure both initial_candidates.json and after_candidates.json exist in reports/")
        return

    diff = list(difflib.unified_diff(a, b, fromfile="initial_candidates.json", tofile="after_candidates.json", lineterm=""))
    if not diff:
        print("No differences found.")
        with open(OUT, "w", encoding="utf8") as f:
            f.write("# Comparison: initial vs after\n\nNo differences found.\n")
        return

    # Write markdown file and include a short header
    header = [
        "# Candidate comparison — initial vs after",
        "",
        "This file contains a unified diff between `reports/initial_candidates.json` and `reports/after_candidates.json`.",
        "",
        "## Diff (unified):",
        "```diff"
    ]
    footer = ["```"]
    with open(OUT, "w", encoding="utf8") as f:
        f.write("\n".join(header + diff + footer))
    print(f"Wrote diff to {OUT}. Lines changed: {len(diff)}")

if __name__ == "__main__":
    main()
