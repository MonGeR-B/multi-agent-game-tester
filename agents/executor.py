import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import traceback

OUT_DIR = Path("reports") / "runs"

class ExecutorAgent:
    def __init__(self, name: str):
        self.name = name

    async def run_test(self, test_case: dict, run_id: str, timeout: int = 15000) -> dict:
        tid = test_case.get("id", "unknown")
        ts = datetime.utcnow().isoformat()
        artifact_dir = OUT_DIR / run_id / tid
        artifact_dir.mkdir(parents=True, exist_ok=True)

        console_lines = []
        screenshot_path = artifact_dir / "screenshot.png"
        dom_path = artifact_dir / "dom.html"
        debug_path = artifact_dir / "executor_debug.log"

        page = None
        browser = None
        ok = False
        err = None

        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Collect console messages
                page.on("console", lambda msg: console_lines.append(f"[{msg.type}] {msg.text}"))

                # Execute test steps
                try:
                    for step in test_case.get("steps", []):
                        action = step.get("action")
                        # inside the step loop, replace load handling with this:
                        if action == "load":
                            url = step.get("url")
                            try:
                                await page.goto(url, timeout=timeout)
                            except Exception as nav_ex:
                                # navigation failed (DNS, network, SSL, blocked, etc.)
                                nav_msg = f"navigation failed for {url}: {repr(nav_ex)}"
                                console_lines.append(f"[error] {nav_msg}")
                                # set err so the executor knows this run failed due to unreachable target
                                err = nav_msg
                                # continue to next steps (we still try to capture screenshot/DOM later)
                                # break out of step loop? we continue so that executor still attempts
                                # to capture what it can (blank page or previous content)

                        elif action == "fill":
                            sel = step.get("selector")
                            val = str(step.get("value", ""))
                            try:
                                await page.wait_for_selector(sel, timeout=3000)
                                await page.fill(sel, val, timeout=timeout)
                            except Exception:
                                # Fallback to JS fill
                                try:
                                    await page.evaluate(
                                        f"document.querySelector('{sel}') && (document.querySelector('{sel}').value = `{val}`)"
                                    )
                                except Exception:
                                    console_lines.append(f"[warn] failed to fill {sel}")
                        elif action == "click":
                            sel = step.get("selector")
                            try:
                                await page.wait_for_selector(sel, timeout=3000)
                                await page.click(sel, timeout=timeout)
                            except Exception:
                                console_lines.append(f"[warn] failed to click {sel}")
                        await asyncio.sleep(0.25)

                    ok = True
                except Exception as e:
                    import traceback
                    err = f"Executor error: {repr(e)}"
                    console_lines.append(f"[error] {err}")
                    console_lines.append(traceback.format_exc())

                # ✅ Always try to capture screenshot and DOM
                if page:
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    dom_path.write_text(await page.content(), encoding="utf-8")

        except Exception as e:
            err = f"Executor error: {e}"
            console_lines.append(f"[error] {err}")

        finally:
            # Fallback artifact capture if main try block failed
            try:
                if page:
                    if not screenshot_path.exists():
                        await page.screenshot(path=str(screenshot_path), full_page=True)
                    if not dom_path.exists():
                        dom_path.write_text(await page.content(), encoding="utf-8")
            except Exception as e2:
                with open(debug_path, "a", encoding="utf-8") as df:
                    df.write(f"[{datetime.utcnow().isoformat()}] failed extra capture: {e2}\n")

            # Cleanup browser
            try:
                if browser:
                    await browser.close()
            except:
                pass

            # Always write logs
            try:
                (artifact_dir / "console.log").write_text("\n".join(console_lines), encoding="utf-8")
            except:
                pass
            try:
                with open(debug_path, "a", encoding="utf-8") as df:
                    df.write(f"[{datetime.utcnow().isoformat()}] ok={ok} err={err}\n")
            except:
                pass

        result = {
            "test_id": tid,
            "executor": self.name,
            "started_at": ts,
            "verdict": "unknown",
            "ok": ok,
            "error": err,
            "artifacts": {
                "console": str((artifact_dir / "console.log").as_posix()) if (artifact_dir / "console.log").exists() else None,
                "screenshot": str(screenshot_path.as_posix()) if screenshot_path.exists() else None,
                "dom": str(dom_path.as_posix()) if dom_path.exists() else None,
                "debug": str(debug_path.as_posix()) if debug_path.exists() else None
            }
        }
        return result
