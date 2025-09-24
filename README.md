🎮 Multi-Agent Game Tester (POC)

An AI-powered automated game testing system built with LangChain, FastAPI, and Streamlit.
The system uses a team of specialized agents to plan, rank, execute, and analyze test cases on any target game website.

🚀 Features

PlannerAgent (LLM + LangChain) → generates 20+ candidate test cases from a target URL.

RankerAgent → filters and selects the most promising test cases.

ExecutorAgents + Orchestrator → run tests in parallel with Playwright, capturing artifacts.

AnalyzerAgent → validates results with repeat runs, reproducibility checks, and triage notes.

Artifact Capture → console logs, DOM snapshots, screenshots (for reachable sites).

Backend → FastAPI with endpoints: /plan, /rank, /execute, /report.

Frontend → Streamlit UI to trigger workflows and view reports interactively.

Reports → JSON output + UI summary table with verdicts, reproducibility stats, and artifact links.

🛠️ Tech Stack

LLM / LangChain → intelligent test case generation.

FastAPI → backend REST API.

Playwright → browser automation (screenshots, DOM, logs).

Streamlit → frontend for interactive testing.

Python 3.10+

📂 Project Structure
multi-agent-game-tester/
│── agents/             # Planner, Ranker, Executor, Orchestrator, Analyzer
│── reports/            # Run outputs (candidates, ranked, reports, artifacts)
│── ui/                 # Streamlit frontend
│── main.py             # FastAPI entrypoint
│── requirements.txt    # Python dependencies
│── README.md

⚡ Quickstart
1. Clone repo & setup venv
git clone https://github.com/MonGer-B/multi-agent-game-tester.git
cd multi-agent-game-tester
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt

2. Install Playwright browser
playwright install chromium

3. Run backend (FastAPI)
uvicorn main:app --reload --port 8000


Backend available at → http://127.0.0.1:8000/docs

4. Run frontend (Streamlit)
streamlit run ui/ui.py


Frontend available at → http://localhost:8501

🧪 Example Workflow

Plan → Generate 20+ candidate tests for a URL.

Rank → Select top-k best candidates.

Execute → Run tests, capture console logs, screenshots, DOM.

Report → View JSON report with verdicts, reproducibility, and triage notes.

🔹 Try with a reachable site (e.g. https://example.com/) to see screenshots in reports.