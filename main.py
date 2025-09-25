import os
import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from agents.planner import PlannerAgent
from agents.orchestrator import OrchestratorAgent
from agents.ranker import RankerAgent
from agents.analyzer import AnalyzerAgent

RUNS_DIR = "reports/runs"
os.makedirs(RUNS_DIR, exist_ok=True)

app = FastAPI(title="Multi-Agent Game Tester POC")

class PlanRequest(BaseModel):
    target_url: str
    num_candidates: int = 20
    speed: Optional[int] = None

@app.post("/plan")
async def plan(req: PlanRequest):
    planner = PlannerAgent()
    candidates = await planner.generate_tests(req.target_url, req.num_candidates, seed=req.speed)
    run_id = str(uuid.uuid4())
    payload = {
        "run_id": run_id,
        "label": req.target_url.replace("https://", ""),
        "target_url": req.target_url,
        "generated_at": datetime.utcnow().isoformat(),
        "candidates": candidates
    }
    safe_name = req.target_url.replace("https://", "").replace("/", "_")
    path = os.path.join(RUNS_DIR, f"{safe_name}_{run_id}_candidates.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return {"run_id": run_id, "candidates_count": len(candidates)}

@app.post("/rank")
async def rank(run_id: str, top_k: int = 10):
    matches = [f for f in os.listdir(RUNS_DIR) if f.endswith(f"{run_id}_candidates.json")]
    if not matches:
        raise HTTPException(status_code=404, detail="Run not found")
    candidates_path = os.path.join(RUNS_DIR, matches[0])

    with open(candidates_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ranker = RankerAgent()
    ranked = ranker.rank_and_select(data["candidates"], top_k=top_k)
    data["top_k"] = ranked

    out_path = os.path.join(RUNS_DIR, f"{run_id}_ranked.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return {"run_id": run_id, "selected": len(ranked)}

@app.post("/execute")
async def execute(run_id: str, background: BackgroundTasks):
    matches = [f for f in os.listdir(RUNS_DIR) if f.endswith(f"{run_id}_ranked.json")]
    if not matches:
        raise HTTPException(status_code=404, detail="Ranked run not found")
    ranked_path = os.path.join(RUNS_DIR, matches[0])

    background.add_task(_execute_run, run_id, ranked_path)
    return {"status": "started", "run_id": run_id}

async def _execute_run(run_id: str, ranked_path: str):
    with open(ranked_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    top_k = data.get("top_k", [])
    orchestrator = OrchestratorAgent()
    results = await orchestrator.execute_tests(top_k, run_id)
    analyzer = AnalyzerAgent()
    report = analyzer.analyze_run(run_id, data, results)

    out_path = os.path.join(RUNS_DIR, f"{run_id}_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

@app.get("/report/{run_id}")
async def get_report(run_id: str):
    matches = [f for f in os.listdir(RUNS_DIR) if f.endswith(f"{run_id}_report.json")]
    if not matches:
        raise HTTPException(status_code=404, detail="Report not found")
    path = os.path.join(RUNS_DIR, matches[0])
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data 
