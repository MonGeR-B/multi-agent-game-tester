# scripts/generate_after.py
import asyncio, json, os
from agents.planner import PlannerAgent

OUT = "reports"
os.makedirs(OUT, exist_ok=True)

async def main():
    planner = PlannerAgent()
    candidates = await planner.generate_tests("https://play.ezygamers.com/", n=20, seed=123, use_rag=True)
    path = os.path.join(OUT, "after_candidates.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2)
    print("Wrote", path)

if __name__ == "__main__":
    asyncio.run(main())
