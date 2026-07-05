from app.database import get_db


def clear_demo_data(conn):
    conn.execute("DELETE FROM audit_log")
    conn.execute("DELETE FROM life_events")
    conn.execute("DELETE FROM holdings")
    conn.execute("DELETE FROM transactions")
    conn.execute("DELETE FROM customers")


def seed_job_change_scenario():
    """Priya gets a salary hike from a new employer."""
    conn = get_db()
    clear_demo_data(conn)

    conn.execute(
        "INSERT INTO customers (id, name) VALUES (?, ?)",
        ("priya", "Priya Sharma"),
    )

    txs = [
        ("2026-01-01", "Salary - Old Corp", 45000, "salary"),
        ("2026-02-01", "Salary - Old Corp", 45000, "salary"),
        ("2026-03-01", "Salary - Old Corp", 45000, "salary"),
        ("2026-04-01", "Salary - TechNova Pvt Ltd", 55000, "salary"),
        ("2026-05-01", "Salary - TechNova Pvt Ltd", 55000, "salary"),
    ]
    for date, desc, amount, cat in txs:
        conn.execute(
            "INSERT INTO transactions (customer_id, date, description, amount, category) VALUES (?, ?, ?, ?, ?)",
            ("priya", date, desc, amount, cat),
        )

    conn.execute(
        "INSERT INTO holdings (customer_id, product_type, details) VALUES (?, ?, ?)",
        ("priya", "SIP", '{"fund": "SBI Bluechip", "monthly": 500}'),
    )

    conn.commit()
    conn.close()


def seed_fd_maturity_scenario():
    """Rahul has an FD maturing in 5 days."""
    conn = get_db()
    clear_demo_data(conn)

    conn.execute(
        "INSERT INTO customers (id, name) VALUES (?, ?)",
        ("rahul", "Rahul Mehta"),
    )

    conn.execute(
        "INSERT INTO transactions (customer_id, date, description, amount, category) VALUES (?, ?, ?, ?, ?)",
        ("rahul", "2026-06-01", "FD interest credit", 12000, "interest"),
    )

    conn.execute(
        "INSERT INTO holdings (customer_id, product_type, details) VALUES (?, ?, ?)",
        (
            "rahul",
            "FD",
            '{"amount": 200000, "rate": 7.1, "maturity_date": "2026-07-09", "days_to_maturity": 5}',
        ),
    )

    conn.commit()
    conn.close()
