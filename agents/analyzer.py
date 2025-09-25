from datetime import datetime

class AnalyzerAgent:
    def analyze_run(self, run_id: str, run_metadata: dict, executor_results: list) -> dict:
        summary = []
        for item in executor_results:
            tid = item.get("test_id")
            runs = item.get("runs", [])
            run_pass = [1 if (r.get("ok") and not r.get("error")) else 0 for r in runs]
            passes = sum(run_pass)
            total = len(runs)
            reproducibility = round(passes / total, 3) if total > 0 else 0.0
            verdict = "pass" if passes > total / 2 else "fail"

            rep_executor = None
            for r in runs:
                if r.get("executor"):
                    rep_executor = r.get("executor")
                    break

            triage = []
            if verdict == "fail":
                if any(r.get("error") for r in runs):
                    triage.append("runtime error or selector mismatch — inspect console and error fields")
                else:
                    triage.append("non-deterministic failure — consider retrying with different timing")
            else:
                if reproducibility < 1.0:
                    triage.append("flaky: passed on some runs, investigate timing/async issues")
                else:
                    triage.append("stable pass")

            artifacts = {}
            for r in runs:
                art = r.get("artifacts", {})
                if art.get("console") and not artifacts.get("console"):
                    artifacts["console"] = art.get("console")
                if art.get("screenshot") and not artifacts.get("screenshot"):
                    artifacts["screenshot"] = art.get("screenshot")
                if art.get("dom") and not artifacts.get("dom"):
                    artifacts["dom"] = art.get("dom")
                if artifacts:
                    break

            summary.append({
                "test_id": tid,
                "verdict": verdict,
                "reproducibility": reproducibility,
                "runs_count": total,
                "passes": passes,
                "triage": triage,
                "executor": rep_executor,
                "artifacts": artifacts
            })

        stats = {"total": len(summary), "passed": sum(1 for s in summary if s["verdict"] == "pass"), "failed": sum(1 for s in summary if s["verdict"] == "fail")}

        report = {
            "run_id": run_id,
            "target_url": run_metadata.get("target_url"),
            "generated_at": run_metadata.get("generated_at"),
            "analyzed_at": datetime.utcnow().isoformat(),
            "summary": summary,
            "stats": stats,
            "notes": ["Analyzer: reproducibility based on repeating each test; triage notes are heuristic."]
        }

        return report
