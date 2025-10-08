# generate_after.py
"""
Generate 'after' (post-RAG ingestion) candidates and save to:
  reports/after_candidates.json

If you want this script to run ingestion first, uncomment the os.system(...) line below
and ensure scripts/ingest_knowledge.py works in your environment.
"""
import json
import os
from datetime import datetime

try:
    from agents.planner import PlannerAgent
except Exception as e:
    raise ImportError("Cannot import agents.planner.PlannerAgent — check file path") from e

OUT_DIR = "reports"
OUT_FILE = os.path.join(OUT_DIR, "after_candidates.json")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # OPTIONAL: run ingestion before generating "after" candidates
    # uncomment the next line if you want this script to call ingestion automatically.
    # os.system("python scripts/ingest_knowledge.py")

    print("Generating after candidates (after RAG ingestion)...")
    planner = PlannerAgent()
    candidates = planner.generate_tests("https://play.ezygamers.com/", n=20)
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
