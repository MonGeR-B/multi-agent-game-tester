# generate_before.py
"""
Generate 'before' (initial) candidates using the Planner and save to:
  reports/initial_candidates.json
"""
import json
import os
from datetime import datetime

# change import path if your planner location is different
try:
    from agents.planner import PlannerAgent
except Exception as e:
    raise ImportError("Cannot import agents.planner.PlannerAgent — check file path") from e

OUT_DIR = "reports"
OUT_FILE = os.path.join(OUT_DIR, "initial_candidates.json")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Generating initial candidates (before RAG ingestion)...")
    # call planner: tweak n or target_url as needed
    planner = PlannerAgent()
    candidates = planner.generate_tests("https://play.ezygamers.com/", n=20)
    # add metadata
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "target_url": "https://play.ezygamers.com/",
        "candidates": candidates
    }
    with open(OUT_FILE, "w", encoding="utf8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Saved {OUT_FILE} (count={len(candidates)})")

if __name__ == "__main__":
    main()
