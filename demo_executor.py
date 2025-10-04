import asyncio
import json
import uuid
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

OUT_DIR = Path("reports/runs")

async def run_test_case(test_case: dict, run_id: str, case_index: int):
    artifact_dir = OUT_DIR / run_id / f"t{case_index+1}"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    video_dir = artifact_dir / "video"
    video_dir.mkdir(exist_ok=True)

    console_lines = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # headful so video works
        # record video into this run/case
        context = await browser.new_context(record_video_dir=str(video_dir), record_video_size={"width": 1280, "height": 720})
        page = await context.new_page()

        page.on("console", lambda msg: console_lines.append(f"[{msg.type}] {msg.text}"))

        try:
            for step in test_case.get("steps", []):
                action = step.get("action")
                if action == "load":
                    url = step.get("url")
                    await page.goto(url, timeout=30000, wait_until="load")
                elif action == "fill":
                    sel = step.get("selector")
                    val = step.get("value", "")
                    try:
                        await page.fill(sel, val, timeout=5000)
                    except Exception:
                        # fallback to JS with correct single argument object
                        await page.evaluate(
                            """({selector, value}) => {
                                const el = document.querySelector(selector);
                                if (el) el.value = value;
                            }""",
                            {"selector": sel, "value": val}
                        )
                elif action == "click":
                    sel = step.get("selector")
                    try:
                        await page.click(sel, timeout=5000)
                    except Exception:
                        # try JS click fallback, single argument so no change
                        await page.evaluate(
                            """(selector) => {
                                const el = document.querySelector(selector);
                                if (el) el.click();
                            }""",
                            sel
                        )

            # capture artifacts
            screenshot_path = artifact_dir / "screenshot.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)

            dom_path = artifact_dir / "dom.html"
            dom = await page.content()
            dom_path.write_text(dom, encoding="utf-8")

            console_path = artifact_dir / "console.log"
            console_path.write_text("\n".join(console_lines), encoding="utf-8")

            # Playwright saves a video file in video_dir, find it and move to artifact dir root
            await context.close()
            await browser.close()

            # find video file (Playwright writes something like video.webm inside video_dir)
            videos = list(video_dir.glob("**/*.webm"))
            if videos:
                videos[0].rename(artifact_dir / "video.webm")

            # write a small report
            report = {
                "test_id": test_case.get("id"),
                "description": test_case.get("description"),
                "started_at": datetime.utcnow().isoformat(),
                "artifacts": {
                    "screenshot": str(screenshot_path),
                    "dom": str(dom_path),
                    "console": str(console_path),
                    "video": str((artifact_dir / "video.webm")) if (artifact_dir / "video.webm").exists() else None
                }
            }
            (artifact_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
            return True, None
        except Exception as e:
            try:
                await browser.close()
            except:
                pass
            return False, str(e)


async def main():
    # small demo: import your planner or use manual tests
    from agents.planner import PlannerAgent
    planner = PlannerAgent()
    targets = await planner.generate_tests("https://play.ezygamers.com", n=3, seed=1234)

    run_id = str(uuid.uuid4())
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for i, t in enumerate(targets):
        ok, err = await run_test_case(t, run_id, i)
        results.append({"test_id": t["id"], "ok": ok, "error": err})

    # write run summary
    summary = {
        "run_id": run_id,
        "started_at": datetime.utcnow().isoformat(),
        "results": results
    }
    (OUT_DIR / run_id / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Done. Run directory:", OUT_DIR / run_id)

if __name__ == "__main__":
    asyncio.run(main())
