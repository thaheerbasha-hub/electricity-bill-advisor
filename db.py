"""
db.py · SQLite database for Power Bill Coach
Tables:
  - users (id, name, phone, pin_hash)
  - bills (id, user_id, month, units, days, estimated, fuel_rs, free_units, load_kw)

Shared helpers:
  - add_user(name, phone, pin)
  - check_login(phone, pin)
  - add_bill(user_id, month, units, days, estimated, fuel_rs, free_units, load_kw)
  - get_bills(user_id)
  - delete_bill(bill_id, user_id)
"""

import hashlib
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "power_coach.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_pin(pin: str) -> str:
    salt = "karnataka_bescom_salt_2026"
    return hashlib.sha256(f"{salt}_{pin}".encode("utf-8")).hexdigest()


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        pin_hash TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        month TEXT NOT NULL,
        units REAL NOT NULL,
        days INTEGER NOT NULL,
        estimated INTEGER NOT NULL DEFAULT 0,
        fuel_rs REAL NOT NULL DEFAULT 0.0,
        free_units REAL,
        load_kw REAL NOT NULL DEFAULT 2.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    conn.commit()

    # Seed the ready-made demo user if not present
    seed_demo_user(conn)
    conn.close()


def seed_demo_user(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE phone = ?", ("9876543210",))
    demo = cur.fetchone()
    if not demo:
        pin_h = hash_pin("1234")
        cur.execute(
            "INSERT INTO users (name, phone, pin_hash) VALUES (?, ?, ?)",
            ("Ramesh Kumar (Demo)", "9876543210", pin_h)
        )
        user_id = cur.lastrowid

        # 6 sample bills leading up to the Dasara festival / vacation jump
        sample_bills = [
            ("May 2026", 152.0, 30, 0, 0.35, 150.0, 2.0),
            ("Jun 2026", 160.0, 31, 0, 0.35, 150.0, 2.0),
            ("Jul 2026", 148.0, 30, 0, 0.35, 150.0, 2.0),
            ("Aug 2026", 155.0, 31, 0, 0.37, 150.0, 2.0),
            ("Sep 2026", 168.0, 30, 0, 0.37, 150.0, 2.0),
            ("Oct 2026", 206.0, 31, 0, 0.37, 150.0, 2.0),  # Crossed 200 GJ limit!
        ]
        for b in sample_bills:
            cur.execute("""
            INSERT INTO bills (user_id, month, units, days, estimated, fuel_rs, free_units, load_kw)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, b[0], b[1], b[2], b[3], b[4], b[5], b[6]))
        conn.commit()


def add_user(name: str, phone: str, pin: str) -> bool:
    phone = phone.strip()
    name = name.strip()
    pin = pin.strip()
    if len(phone) < 10 or not pin:
        return False
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, phone, pin_hash) VALUES (?, ?, ?)",
            (name, phone, hash_pin(pin))
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def check_login(phone: str, pin: str):
    phone = phone.strip()
    pin = pin.strip()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, phone, pin_hash FROM users WHERE phone = ?",
        (phone,)
    )
    row = cur.fetchone()
    conn.close()
    if row and row["pin_hash"] == hash_pin(pin):
        return {"id": row["id"], "name": row["name"], "phone": row["phone"]}
    return None


def add_bill(user_id: int, month: str, units: float, days: int, estimated: bool, fuel_rs: float, free_units: float, load_kw: float):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO bills (user_id, month, units, days, estimated, fuel_rs, free_units, load_kw)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, month.strip(), float(units), int(days), 1 if estimated else 0, float(fuel_rs), free_units, float(load_kw)))
    conn.commit()
    conn.close()


def get_bills(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, month, units, days, estimated, fuel_rs, free_units, load_kw, created_at
    FROM bills
    WHERE user_id = ?
    ORDER BY id ASC
    """, (user_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def delete_bill(bill_id: int, user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM bills WHERE id = ? AND user_id = ?", (bill_id, user_id))
    conn.commit()
    conn.close()


# Initialize table on import
init_db()
