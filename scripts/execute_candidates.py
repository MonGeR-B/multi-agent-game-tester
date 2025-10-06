import asyncio, json, os, uuid, sys
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

OUT_ROOT = Path("reports/runs")

async def run_test_case(test_case: dict, run_dir: Path, case_index: int):
    artifact_dir = run_dir / f"t{case_index+1}"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    video_dir = artifact_dir / "video"
    video_dir.mkdir(exist_ok=True)
    console_lines = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(record_video_dir=str(video_dir), record_video_size={"width":1280,"height":720})
        page = await context.new_page()
        page.on("console", lambda msg: console_lines.append(f"[{msg.type}] {msg.text}"))

        try:
            for step in test_case.get("steps", []):
                action = step.get("action")

                if action == "load":
                    url = step.get("url")
                    if url is None:
                        print("Skipping load step due to missing URL")
                        continue
                    await page.goto(url, timeout=30000, wait_until="load")

                elif action == "fill":
                    sel = step.get("selector")
                    val = step.get("value", "")
                    if sel is None:
                        print("Skipping fill step due to missing selector")
                        continue
                    val = str(val)
                    try:
                        await page.fill(sel, val, timeout=5000)
                    except Exception:
                        await page.evaluate(
                            "({selector, value}) => { const el = document.querySelector(selector); if (el) el.value = value; }",
                            {"selector": sel, "value": val}
                        )

                elif action == "click":
                    sel = step.get("selector")
                    if sel is None:
                        print("Skipping click step due to missing selector")
                        continue
                    try:
                        await page.click(sel, timeout=5000)
                    except Exception:
                        await page.evaluate(
                            "(s) => { const el = document.querySelector(s); if (el) el.click(); }",
                            sel,
                        )

                elif action == "sleep":
                    import asyncio as _a
                    await _a.sleep(step.get("duration", 0.5))

            # capture screenshot + dom + console
            screenshot = artifact_dir / "screenshot.png"
            await page.screenshot(path=str(screenshot), full_page=True)
            dom_html = artifact_dir / "dom.html"
            dom_html.write_text(await page.content(), encoding="utf-8")
            console_log = artifact_dir / "console.log"
            console_log.write_text("\n".join(console_lines), encoding="utf-8")

            await context.close()
            await browser.close()

            # move video file if exists
            vids = list(video_dir.glob("**/*.webm"))
            if vids:
                vids[0].rename(artifact_dir / "video.webm")

            # write simple report.json
            report = {
                "test_id": test_case.get("id"),
                "description": test_case.get("description"),
                "artifacts": {
                    "screenshot": str(screenshot) if screenshot.exists() else None,
                    "dom": str(dom_html) if dom_html.exists() else None,
                    "console": str(console_log) if console_log.exists() else None,
                    "video": str((artifact_dir / "video.webm")) if (artifact_dir / "video.webm").exists() else None
                },
                "ok": True
            }
            (artifact_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
            return True, None

        except Exception as e:
            try:
                await browser.close()
            except:
                pass
            return False, str(e)


async def main(candidates_file: str, top_k: int = 5, run_label: str | None = None):
    if not Path(candidates_file).exists():
        print("Candidates file not found:", candidates_file)
        return
    with open(candidates_file, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    top = candidates[:top_k]
    run_id = run_label or f"run_{uuid.uuid4().hex[:8]}"
    run_dir = OUT_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for i, tc in enumerate(top):
        print("Running test", i + 1, tc.get("id"))
        ok, err = await run_test_case(tc, run_dir, i)
        results.append({"test_id": tc.get("id"), "ok": ok, "error": err})
    summary = {"run_id": run_id, "started_at": datetime.utcnow().isoformat(), "results": results}
    (run_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Done. Run dir:", run_dir)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="candidates JSON file")
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--label", default="run_initial")
    args = parser.parse_args()
    asyncio.run(main(args.file, args.top, args.label))
