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

## 3-minute judge demo script

1. **Intro (30s)** — Point to header: Arthasathi, Digital Engagement pillar, multi-agent pipeline
2. **Job change (60s)** — Click scenario → pipeline animates → show salary highlight → phone nudge → Approve
3. **FD maturity (60s)** — Switch scenario → reinvestment options → Approve → audit trail
4. **Close (30s)** — Optional: toggle DPDP consent to show compliance block; emphasize scale + RBI/DPDP readiness

Presenter hints appear in the yellow bar at the top during the demo.

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
