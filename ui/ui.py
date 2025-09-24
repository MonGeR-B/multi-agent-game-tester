import streamlit as st
import requests
from pathlib import Path
import time
import json


API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Multi-Agent Tester", layout="wide")
st.title("⚡ Multi-Agent Game Tester")

st.sidebar.header("Settings")
target_url = st.sidebar.text_input("Target URL", "https://play.ezygamer.com/")
num_candidates = st.sidebar.number_input("Number of candidates", min_value=5, max_value=50, value=10)
top_k = st.sidebar.number_input("Top K", min_value=1, max_value=20, value=5)

if "run_id" not in st.session_state:
    st.session_state["run_id"] = None

st.subheader("1️⃣ Plan Tests")
if st.button("Generate Candidates"):
    with st.spinner("Generating test candidates..."):
        resp = requests.post(f"{API_URL}/plan", json={
            "target_url": target_url,
            "num_candidates": num_candidates
        })
    if resp.status_code == 200:
        data = resp.json()
        st.session_state["run_id"] = data.get("run_id")
        st.success(f"Generated {data.get('candidates_count', 'N/A')} candidates. Run ID: {data.get('run_id')}")
    else:
        st.error(f"Error generating candidates: {resp.text}")

st.subheader("2️⃣ Rank Candidates")
if st.button("Rank Top-k"):
    rid = st.session_state.get("run_id")
    if not rid:
        st.warning("Please generate candidates first.")
    else:
        with st.spinner("Ranking candidates..."):
            resp = requests.post(f"{API_URL}/rank", params={"run_id": rid, "top_k": top_k})
        if resp.status_code == 200:
            data = resp.json()
            st.success(f"Selected {data.get('selected', 'N/A')} top tests for run {rid}")
        else:
            st.error(f"Error ranking candidates: {resp.text}")

st.subheader("3️⃣ Execute Tests")
if st.button("Execute"):
    rid = st.session_state.get("run_id")
    if not rid:
        st.warning("Please generate and rank candidates first.")
    else:
        with st.spinner("Executing tests..."):
            resp = requests.post(f"{API_URL}/execute", params={"run_id": rid})
        if resp.status_code == 200:
            st.info("Execution started. Please wait a few seconds before fetching the report.")
        else:
            st.error(f"Error executing tests: {resp.text}")

st.subheader("4️⃣ Fetch Report")
if st.button("Fetch Report"):
    rid = st.session_state.get("run_id")
    if not rid:
        st.warning("Please execute tests first.")
    else:
        report = None
        for i in range(5):
            resp = requests.get(f"{API_URL}/report/{rid}")
            if resp.status_code == 200:
                try:
                    report = resp.json()
                except Exception as e:
                    st.error(f"Failed to parse JSON response: {e}")
                    st.text(resp.text)
                    report = None
                break
            else:
                st.info(f"Report not ready yet (attempt {i+1}/5)...")
                time.sleep(2)

        if not report:
            st.error("❌ Report not found or invalid after retries.")
        elif isinstance(report, dict) and "summary" in report:
            st.success("Report fetched successfully ✅")

            st.write("### 📝 Full Report JSON")
            st.json(report)

            summary = report.get("summary", [])
            if not summary:
                st.warning("Report fetched, but summary is empty.")
            else:
                flat_summary = []
                for s in summary:
                    executor = s.get("executor")
                    if not executor:
                        runs = s.get("runs") or s.get("runs_details") or None
                        if runs and isinstance(runs, list) and len(runs) > 0:
                            executor = runs[0].get("executor", "unknown")
                        else:
                            executor = "unknown"

                    triage_val = s.get("triage", [])
                    if isinstance(triage_val, list):
                        triage_str = "; ".join(str(x) for x in triage_val)
                    else:
                        triage_str = str(triage_val)

                    artifacts = s.get("artifacts", {}) or {}
                    flat_summary.append({
                        "test_id": s.get("test_id"),
                        "verdict": s.get("verdict"),
                        "reproducibility": s.get("reproducibility"),
                        "executor": executor,
                        "runs_count": s.get("runs_count", None),
                        "passes": s.get("passes", None),
                        "triage": triage_str,
                        "console_log": artifacts.get("console"),
                        "screenshot": artifacts.get("screenshot"),
                        "dom": artifacts.get("dom")
                    })

                st.write("### 📊 Summary Table")
                st.dataframe(flat_summary)

                stats = report.get("stats", {})
                if stats:
                    st.write("### 📈 Pass/Fail Stats")
                    chart_data = {"Passed": [stats.get("passed", 0)], "Failed": [stats.get("failed", 0)]}
                    st.bar_chart(chart_data)

                # Show artifacts content (safe)
                st.write("### 📦 Artifacts")
                for s in summary:
                    tid = s.get("test_id")
                    verdict = s.get("verdict")
                    st.markdown(f"**Test {tid} ({verdict})**")
                    artifacts = s.get("artifacts", {}) or {}

                    console_path = artifacts.get("console")
                    screenshot_path = artifacts.get("screenshot")
                    dom_path = artifacts.get("dom")

                    if console_path:
                        p_console = Path(console_path)
                        if p_console.exists():
                            with open(p_console, "r", encoding="utf-8") as f:
                                st.code(f.read(), language="bash")
                        else:
                            st.warning(f"Console log path listed but file not found: {console_path}")
                    else:
                        st.info("No console log recorded for this test.")

                    if screenshot_path:
                        p_shot = Path(screenshot_path)
                        if p_shot.exists():
                            st.image(str(p_shot))
                        else:
                            st.warning(f"Screenshot path listed but file not found: {screenshot_path}")
                    else:
                        st.info("No screenshot recorded for this test.")

                    if dom_path:
                        p_dom = Path(dom_path)
                        if p_dom.exists():
                            with open(p_dom, "r", encoding="utf-8") as f:
                                dom_text = f.read()
                                st.text(dom_text[:400] + ("\n\n... (truncated)" if len(dom_text) > 400 else ""))
                        else:
                            st.warning(f"DOM path listed but file not found: {dom_path}")
                    else:
                        st.info("No DOM snapshot recorded for this test.")

        else:
            st.error("❌ Invalid report structure or missing 'summary'.")
            try:
                st.text(resp.text)
            except Exception:
                pass


