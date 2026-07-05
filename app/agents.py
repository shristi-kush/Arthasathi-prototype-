import json

from app.database import get_db


def log_audit(conn, life_event_id, agent, message):
    conn.execute(
        "INSERT INTO audit_log (life_event_id, agent, message) VALUES (?, ?, ?)",
        (life_event_id, agent, message),
    )


# --- Observer: rule-based detection ---

def observe_job_change(conn, customer_id):
    rows = conn.execute(
        "SELECT description, amount FROM transactions WHERE customer_id = ? AND category = 'salary' ORDER BY date",
        (customer_id,),
    ).fetchall()

    if len(rows) < 2:
        return None

    old_avg = sum(r["amount"] for r in rows[:-2]) / max(len(rows) - 2, 1)
    latest = rows[-1]["amount"]
    new_employer = rows[-1]["description"]

    if old_avg > 0 and latest > old_avg * 1.15 and "Old" not in new_employer:
        pct = round((latest - old_avg) / old_avg * 100)
        return {
            "event_type": "JOB_CHANGE",
            "confidence": 0.87,
            "evidence": [
                f"Salary increased by {pct}%",
                f"New source: {new_employer}",
                f"Latest credit: ₹{latest:,.0f}",
            ],
        }
    return None


def observe_fd_maturity(conn, customer_id):
    row = conn.execute(
        "SELECT details FROM holdings WHERE customer_id = ? AND product_type = 'FD'",
        (customer_id,),
    ).fetchone()

    if not row:
        return None

    fd = json.loads(row["details"])
    days = fd.get("days_to_maturity", 999)

    if days <= 7:
        return {
            "event_type": "FD_MATURITY",
            "confidence": 0.95,
            "evidence": [
                f"FD of ₹{fd['amount']:,.0f} matures in {days} days",
                f"Current rate: {fd['rate']}%",
                f"Maturity date: {fd['maturity_date']}",
            ],
        }
    return None


def run_observer(customer_id):
    conn = get_db()
    events = []

    job = observe_job_change(conn, customer_id)
    if job:
        events.append(job)

    fd = observe_fd_maturity(conn, customer_id)
    if fd:
        events.append(fd)

    conn.close()
    return events


# --- Planner: template-based plans ---

PLANS = {
    "JOB_CHANGE": {
        "message": "Congratulations! It looks like your income went up. Would you like to step up your SIP from ₹500 to ₹1,500/month?",
        "action": "SIP_STEP_UP",
    },
    "FD_MATURITY": {
        "message": "Your FD of ₹2,00,000 matures in 5 days. Pick a reinvestment option:",
        "action": "FD_REINVEST",
    },
}


def run_planner(event_type):
    return PLANS.get(event_type, {"message": "We have a suggestion for you.", "action": "GENERIC"})


# --- Compliance: simple rules ---

def run_compliance(customer, hypothesis, plan):
    reasons = []

    if not customer["consent_offers"]:
        return "BLOCKED", "Customer has not consented to proactive offers (DPDP)."

    if hypothesis["confidence"] < 0.75:
        return "BLOCKED", "Confidence too low — must ask user to confirm first."

    if plan["action"] == "SIP_STEP_UP" and customer["risk_profile"] == "conservative":
        reasons.append("Conservative profile noted — showing moderate step-up only.")

    # Quiet hours check deferred — enable later for production
    note = " | ".join(reasons) if reasons else "All guardrails passed."
    return "APPROVED", note


# --- Full pipeline ---

def process_customer(customer_id):
    conn = get_db()
    customer = conn.execute(
        "SELECT * FROM customers WHERE id = ?", (customer_id,)
    ).fetchone()

    if not customer:
        conn.close()
        return []

    hypotheses = run_observer(customer_id)
    created = []

    for h in hypotheses:
        plan = run_planner(h["event_type"])
        status, reason = run_compliance(dict(customer), h, plan)

        cur = conn.execute(
            """INSERT INTO life_events
               (customer_id, event_type, confidence, evidence, plan_message, plan_action,
                compliance_status, compliance_reason, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                customer_id,
                h["event_type"],
                h["confidence"],
                json.dumps(h["evidence"]),
                plan["message"],
                plan["action"],
                status,
                reason,
                "approved" if status == "APPROVED" else "pending",
            ),
        )
        event_id = cur.lastrowid

        log_audit(conn, event_id, "Observer", f"Detected {h['event_type']} ({h['confidence']:.0%})")
        log_audit(conn, event_id, "Planner", plan["message"])
        log_audit(conn, event_id, "Compliance", f"{status}: {reason}")

        created.append(event_id)

    conn.commit()
    conn.close()
    return created


def approve_event(event_id):
    conn = get_db()
    event = conn.execute("SELECT * FROM life_events WHERE id = ?", (event_id,)).fetchone()

    if not event or event["compliance_status"] != "APPROVED":
        conn.close()
        return False, "Cannot execute — not approved by compliance."

    action = event["plan_action"]
    result = ""

    if action == "SIP_STEP_UP":
        result = "SIP updated: ₹500 → ₹1,500/month (mock). Nominee review scheduled."
    elif action == "FD_REINVEST":
        result = "FD reinvestment queued: 50% renewed FD + 50% debt SIP (mock)."
    else:
        result = "Action completed (mock)."

    conn.execute("UPDATE life_events SET status = 'completed' WHERE id = ?", (event_id,))
    log_audit(conn, event_id, "Action", result)
    log_audit(conn, event_id, "Human", "Customer approved via OTP (mock).")

    conn.commit()
    conn.close()
    return True, result
