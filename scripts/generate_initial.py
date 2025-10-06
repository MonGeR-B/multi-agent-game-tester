# scripts/generate_initial.py
import asyncio, json, os
from agents.planner import PlannerAgent

OUT = "reports"
os.makedirs(OUT, exist_ok=True)

async def main():
    planner = PlannerAgent()
    # generate without RAG (seed for determinism)
    candidates = await planner.generate_tests("https://play.ezygamers.com/", n=20, seed=42, use_rag=False)
    path = os.path.join(OUT, "initial_candidates.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2)
    print("Wrote", path)

if __name__ == "__main__":
    asyncio.run(main())
