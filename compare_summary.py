# compare_summary.py
"""
Generate a short human-readable summary comparing:
  - reports/initial_candidates.json
  - reports/after_candidates.json

Writes: reports/compare_summary.txt
Also prints a concise summary to stdout.
"""

import json
import os
from statistics import mean

REPORTS_DIR = "reports"
INIT_PATH = os.path.join(REPORTS_DIR, "initial_candidates.json")
AFTER_PATH = os.path.join(REPORTS_DIR, "after_candidates.json")
OUT_PATH = os.path.join(REPORTS_DIR, "compare_summary.txt")


def load_candidates(path):
    if not os.path.exists(path):
        return None
    try:
        j = json.load(open(path, "r", encoding="utf8"))
        # allow either {"candidates": [...]} or [...] top-level
        if isinstance(j, dict) and "candidates" in j:
            return j["candidates"]
        if isinstance(j, list):
            return j
    except Exception:
        return None
    return None


def stats_for(cands):
    if not cands:
        return {}
    counts = {
        "total": len(cands),
        "avg_steps": mean(len(c.get("steps", [])) for c in cands) if cands else 0,
        "wait_count": sum(sum(1 for s in c.get("steps", []) if s.get("action","").lower()=="wait") for c in cands),
        "retry_count": sum(sum(1 for s in c.get("steps", []) if "retry" in (s.get("action","").lower() + " " + str(s.get("selector","")).lower())) for c in cands),
        "unique_selectors": set(s.get("selector","") for c in cands for s in c.get("steps", []) if s.get("selector")),
    }
    counts["unique_selectors_count"] = len([x for x in counts["unique_selectors"] if x])
    return counts


def sample_diffs(init, after, n=3):
    diffs = []
    for i in range(min(len(init), len(after), n)):
        ia = init[i]
        aa = after[i]
        if ia.get("description") != aa.get("description") or ia.get("steps") != aa.get("steps"):
            diffs.append({
                "index": i,
                "before_desc": ia.get("description"),
                "after_desc": aa.get("description"),
                "before_steps": ia.get("steps"),
                "after_steps": aa.get("steps"),
            })
    return diffs


def main():
    init = load_candidates(INIT_PATH)
    after = load_candidates(AFTER_PATH)

    lines = []
    lines.append("Candidate Comparison Summary")
    lines.append("=" * 30)
    lines.append("")

    if init is None:
        lines.append(f"Initial candidates file not found: {INIT_PATH}")
    else:
        s_init = stats_for(init)
        lines.append(f"Initial candidates: {s_init['total']} tests")
        lines.append(f"  - avg steps: {s_init['avg_steps']:.2f}")
        lines.append(f"  - wait steps total: {s_init['wait_count']}")
        lines.append(f"  - retry occurrences (heuristic): {s_init['retry_count']}")
        lines.append(f"  - unique selectors: {s_init['unique_selectors_count']}")
    lines.append("")

    if after is None:
        lines.append(f"After candidates file not found: {AFTER_PATH}")
    else:
        s_after = stats_for(after)
        lines.append(f"After candidates: {s_after['total']} tests")
        lines.append(f"  - avg steps: {s_after['avg_steps']:.2f}")
        lines.append(f"  - wait steps total: {s_after['wait_count']}")
        lines.append(f"  - retry occurrences (heuristic): {s_after['retry_count']}")
        lines.append(f"  - unique selectors: {s_after['unique_selectors_count']}")
    lines.append("")

    # basic improvement heuristics
    if init and after:
        lines.append("Heuristics / observations:")
        if s_after["wait_count"] > s_init["wait_count"]:
            lines.append("  - After: more 'wait' steps found (improved stability suggestions).")
        else:
            lines.append("  - After: no significant increase in 'wait' steps.")

        if s_after["unique_selectors_count"] > s_init["unique_selectors_count"]:
            lines.append("  - After: more unique selectors detected (more targeted actions).")
        else:
            lines.append("  - After: selector diversity unchanged or reduced.")

        if s_after["avg_steps"] > s_init["avg_steps"]:
            lines.append("  - After: tests have more steps on average (more thorough).")
        else:
            lines.append("  - After: average test length unchanged or shorter.")

        # sample diffs
        diffs = sample_diffs(init, after, n=5)
        if diffs:
            lines.append("")
            lines.append("Sample changed tests (first differences):")
            for d in diffs:
                lines.append(f"  - test index {d['index']}:")
                lines.append(f"      before: {d['before_desc']}")
                lines.append(f"      after : {d['after_desc']}")
        else:
            lines.append("No clear first-3 test diffs found; see full JSON files for details.")

    # write
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf8") as f:
        f.write("\n".join(lines))

    # print short summary
    print("\n".join(lines[:30]))
    print(f"\nFull summary written to: {OUT_PATH}")


if __name__ == "__main__":
    main()
