"""
Generate 'before' (initial) candidates using the Planner and save to:
  reports/initial_candidates.json
"""

import json
import os
from datetime import datetime, timezone

from agents.planner import PlannerAgent

OUT_DIR = "reports"
OUT_FILE = os.path.join(OUT_DIR, "initial_candidates.json")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Generating initial candidates (before RAG ingestion)...")
    planner = PlannerAgent()
    # generate with RAG, seed for determinism
    candidates = planner.generate_tests("https://play.ezygamers.com/", n=20, seed=42)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_url": "https://play.ezygamers.com/",
        "candidates": candidates
    }
    with open(OUT_FILE, "w", encoding="utf8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Saved {OUT_FILE} (count={len(candidates)})")

if __name__ == "__main__":
    main()
