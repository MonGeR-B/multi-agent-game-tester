# 🎮 Multi-Agent Game Tester (POC)

An AI-powered automated game testing system built with **LangChain, FastAPI, Playwright, and Streamlit**.  
The system simulates a team of specialized agents to plan, rank, execute, and analyze test cases on any target game website.

---

## 🚀 Features

- **PlannerAgent** (LLM + LangChain) → generates 20+ candidate test cases from a target URL.  
- **RankerAgent** → filters and selects the most promising test cases.  
- **ExecutorAgents + Orchestrator** → run tests in parallel with Playwright, capturing artifacts.  
- **AnalyzerAgent** → validates results with repeat runs, reproducibility checks, and triage notes.  
- **Artifact Capture** → console logs, DOM snapshots, screenshots (when site is reachable).  
- **Backend** → FastAPI with endpoints: `/plan`, `/rank`, `/execute`, `/report`.  
- **Frontend** → Streamlit UI to trigger workflows and view reports interactively.  
- **Reports** → JSON output + UI summary table with verdicts, reproducibility stats, and artifact links.  

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **LangChain** → LLM-powered intelligent test case generation  
- **FastAPI** → backend REST API  
- **Playwright** → browser automation (screenshots, DOM, logs)  
- **Streamlit** → frontend for interactive testing  
- **Uvicorn** → ASGI server for FastAPI  

---

## 📂 Project Structure

multi-agent-game-tester/
│── agents/ # Planner, Ranker, Executor, Orchestrator, Analyzer
│── reports/ # Run outputs (candidates, ranked, reports, artifacts)
│── ui/ # Streamlit frontend
│── main.py # FastAPI entrypoint
│── requirements.txt # Python dependencies
│── README.md # Project documentation

---

## ⚡ Quickstart

### 1. Clone repository & setup environment
```bash
git clone https://github.com/MonGer-B/multi-agent-game-tester.git
cd multi-agent-game-tester

# Create virtual environment
python -m venv .venv

# Activate venv (Windows PowerShell)
.venv\Scripts\Activate.ps1
2. Install dependencies
bash
Copy code
pip install -r requirements.txt
3. Install Playwright browser
bash
Copy code
playwright install chromium
4. Run backend (FastAPI)
bash
Copy code
uvicorn main:app --reload --port 8000
Backend available at → http://127.0.0.1:8000/docs

5. Run frontend (Streamlit)
bash
Copy code
streamlit run ui/ui.py
Frontend available at → http://localhost:8501

🧪 Example Workflow
Plan → Generate 20+ candidate tests for a URL.

Rank → Select top-k best candidates.

Execute → Run tests, capture console logs, screenshots, DOM.

Report → View JSON report with verdicts, reproducibility, and triage notes.

🔹 For testing, use a reachable site such as https://example.com.

🎥 Demo Video
https://www.dropbox.com/scl/fi/gzd9y3yaw37vgi3l83flj/Multi-Agent-Game-Tester_Demo_video.mov?rlkey=cj6xqxszvij5aenmqvn68l6fb&e=2&st=f7qb0gdt&dl=0


👨‍💻 Author
Developed by Baibhab Ghosh
GitHub: MonGer-B

📌 Notes
Screenshots and DOM snapshots require a reachable target website.

If the target site is unreachable, reports will still include logs and artifacts but without screenshots.

This project was built as part of an intern assignment (Multi-Agent Game Tester POC, 5 days).


---

This is 100% polished — once you push this README.md, your repo is submission-ready. ✅  


