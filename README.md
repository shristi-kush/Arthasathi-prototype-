# Arthasathi — Basic Prototype

Proactive life-event financial agent for SBI Hackathon @ GFF 2026.

**Pipeline:** Observer → Planner → Compliance → Action (with human approval)

## Quick start

```bash
cd SBI_hackathon
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

`pip install` is only needed the first time. To stop the server, press `Ctrl + C`.

## How it works

1. Pick a scenario (**Job Change** or **FD Maturity**) to seed synthetic data and run the agent pipeline.
2. The **Observer** detects a life event, the **Planner** drafts a nudge, and the **Compliance** guardrail checks consent and confidence.
3. Approve the nudge to trigger a mock **Action** with a full, explainable audit trail.
4. Toggle DPDP consent to see the compliance guardrail block or allow a nudge.

## What's included

- Rule-based Observer (no LLM / API key needed)
- Template Planner messages
- Compliance guardrails (consent, confidence, quiet hours)
- Mock Action execution
- SQLite database
- Simple single-page UI

## What's deferred (later)

- LLM-powered Planner
- LangGraph orchestration
- More life events (health, school fees)
- Hindi UI
- Real YONO integration
- Separate admin console

## Project structure

```
app/
  main.py       # FastAPI routes + UI
  agents.py     # Observer, Planner, Compliance, Action
  database.py   # SQLite schema
  seed.py       # Demo scenarios
  templates/
    index.html  # Demo UI
```
