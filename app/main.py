import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.agents import approve_event, process_customer
from app.database import get_db, init_db
from app.seed import seed_fd_maturity_scenario, seed_job_change_scenario

app = FastAPI(title="Arthasathi", description="Proactive Life-Event Financial Agent")
templates = Jinja2Templates(directory="app/templates")

init_db()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/seed/{scenario}")
async def seed(scenario: str):
    meta = {
        "job_change": {
            "customer_id": "priya",
            "title": "Job Change",
            "subtitle": "Salary hike detected → SIP step-up",
            "seed": seed_job_change_scenario,
        },
        "fd_maturity": {
            "customer_id": "rahul",
            "title": "FD Maturity",
            "subtitle": "Deposit maturing → reinvestment options",
            "seed": seed_fd_maturity_scenario,
        },
    }
    if scenario not in meta:
        return JSONResponse({"error": "Unknown scenario"}, status_code=400)

    info = meta[scenario]
    info["seed"]()
    event_ids = process_customer(info["customer_id"])
    return {
        "ok": True,
        "customer_id": info["customer_id"],
        "scenario": scenario,
        "title": info["title"],
        "subtitle": info["subtitle"],
        "events_created": event_ids,
    }


@app.get("/api/state")
async def state():
    conn = get_db()

    customer = conn.execute("SELECT * FROM customers LIMIT 1").fetchone()
    events = conn.execute(
        "SELECT * FROM life_events ORDER BY id DESC"
    ).fetchall()
    audit = conn.execute(
        "SELECT * FROM audit_log ORDER BY id"
    ).fetchall()
    txs = conn.execute(
        "SELECT * FROM transactions ORDER BY date"
    ).fetchall()
    holdings = conn.execute(
        "SELECT * FROM holdings ORDER BY id"
    ).fetchall()

    conn.close()

    return {
        "customer": dict(customer) if customer else None,
        "events": [dict(e) for e in events],
        "audit": [dict(a) for a in audit],
        "transactions": [dict(t) for t in txs],
        "holdings": [dict(h) for h in holdings],
    }


@app.post("/api/events/{event_id}/approve")
async def approve(event_id: int):
    ok, message = approve_event(event_id)
    if not ok:
        return JSONResponse({"error": message}, status_code=400)
    return {"ok": True, "message": message}


@app.post("/api/consent/toggle")
async def toggle_consent():
    conn = get_db()
    customer = conn.execute("SELECT * FROM customers LIMIT 1").fetchone()
    if customer:
        new_val = 0 if customer["consent_offers"] else 1
        conn.execute(
            "UPDATE customers SET consent_offers = ? WHERE id = ?",
            (new_val, customer["id"]),
        )
        conn.commit()
    conn.close()
    return {"ok": True}
