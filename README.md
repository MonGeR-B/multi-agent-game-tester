🎮 Multi-Agent Game Tester (RAG-Enabled)

An AI-powered automated game testing system that uses multi-agent collaboration and Retrieval-Augmented Generation (RAG) to plan, execute, and refine test cases dynamically for any web-based game.

Built with LangChain, FastAPI, Playwright, Streamlit, and OpenAI’s GPT models, this project demonstrates an evolving testing agent that learns from past runs to generate more stable, targeted, and realistic tests.

🚀 Key Features
🧩 Multi-Agent Architecture

PlannerAgent → Generates test cases using RAG + LLM context.

RankerAgent → Prioritizes the best candidate tests.

ExecutorAgent & Orchestrator → Run tests in Playwright, collect artifacts.

AnalyzerAgent → Evaluates reproducibility and consistency of results.

🧠 RAG (Retrieval-Augmented Generation)

Uses LangChain + Chroma to store prior reports and knowledge.

Planner retrieves historical test artifacts before creating new ones.

Generates context-aware tests that avoid redundant steps and add stability.

Produces measurable improvement in selectors, waits, and step complexity.

🧾 Reporting

Each test run outputs structured JSONs under reports/runs/.

RAG re-indexes previous runs to continuously improve generation.

Includes comparison and summary scripts for analyzing improvement.

⚙️ Tech Stack
Layer	Tools / Frameworks
Language	Python 3.10+
LLM Interface	LangChain, OpenAI API
Vector DB (RAG)	Chroma with OpenAIEmbeddings
Backend	FastAPI + Uvicorn
Automation	Playwright
Frontend	Streamlit
Data Storage	JSON-based reports + persistent vector store
🧠 RAG Learning Results (Before → After)
Metric	Before RAG	After RAG	Change
Test Cases	20	20	—
Avg Steps per Test	3.0	3.4	⬆ 13.3 %
Wait Steps	0	20	✅ Improved stability
Unique Selectors	2	34	✅ More targeted actions
🔍 Qualitative Improvements

Before → generic validation tests like “Update selectors” or “Analyze console logs”

After → concrete gameplay actions like “Test login,” “Check leaderboard,” “Pause/Resume game.”

System now learns from prior artifacts to refine selectors and add wait steps dynamically.

🧾 Full summary in:
reports/compare_summary.txt

🧪 Example Workflow
# 1. Setup environment
python -m venv .venv
.venv\Scripts\Activate.ps1        # (Windows PowerShell)
pip install -r requirements.txt

# 2. Ingest past runs (RAG data)
python scripts/ingest_knowledge.py

# 3. Generate baseline tests (before RAG)
python generate_before.py

# 4. Generate improved tests (after RAG)
python generate_after.py

# 5. Compare & summarize improvements
python compare_summary.py


Outputs:

reports/initial_candidates.json

reports/after_candidates.json

reports/compare_summary.txt

📂 Project Structure
multi-agent-game-tester/
│
├── agents/
│   ├── planner.py          # PlannerAgent (RAG + LLM)
│   ├── rag.py              # RAG retrieval / QA helper
│   ├── llm_provider.py     # Model abstraction (OpenAI / Gemini / Ollama)
│   └── ...
│
├── reports/
│   ├── runs/               # Raw run outputs
│   ├── initial_candidates.json
│   ├── after_candidates.json
│   ├── compare_summary.txt
│   └── llm_raw_fail.txt
│
├── scripts/
│   ├── ingest_knowledge.py # Build vector store from reports
│
├── ui/
│   └── ui.py               # Streamlit frontend
│
├── main.py                 # FastAPI entrypoint
├── requirements.txt
└── README.md

🧠 Key Learning

This system demonstrates:

How RAG + LLMs can self-improve software testing pipelines.

How test generation quality can be quantitatively measured.

Integration of FastAPI, LangChain, and Playwright into a multi-agent framework.

👨‍💻 Author

Baibhab Ghosh
🔗 GitHub @MonGer-B

📧 AI & Automation Developer | 2025

📌 Notes

Screenshots and DOM snapshots depend on a live, reachable site.

For unreachable targets, logs and structured artifacts are still generated.

Built as part of an internship assignment — Multi-Agent Game Tester (POC + RAG enhancement).

✅ Status: Complete & Submission-Ready
Repo: https://github.com/MonGer-B/multi-agent-game-tester
