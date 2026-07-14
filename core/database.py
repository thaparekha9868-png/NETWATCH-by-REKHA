"""
database.py
Handles all SQLite storage for network metrics and detected anomalies.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "network_metrics.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    latency_ms REAL NOT NULL,
    packet_loss_pct REAL NOT NULL,
    bandwidth_mbps REAL NOT NULL,
    is_anomaly INTEGER DEFAULT 0,
    anomaly_score REAL DEFAULT 0.0
);
"""


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute(SCHEMA)


def insert_metric(latency_ms, packet_loss_pct, bandwidth_mbps, is_anomaly=0, anomaly_score=0.0, timestamp=None):
    timestamp = timestamp or datetime.utcnow().isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO metrics
               (timestamp, latency_ms, packet_loss_pct, bandwidth_mbps, is_anomaly, anomaly_score)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (timestamp, latency_ms, packet_loss_pct, bandwidth_mbps, is_anomaly, anomaly_score),
        )
        return cur.lastrowid


def get_recent_metrics(limit=100):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM metrics ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def get_all_metrics():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM metrics ORDER BY id ASC").fetchall()
    return [dict(r) for r in rows]


def get_anomaly_count():
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as c FROM metrics WHERE is_anomaly = 1"
        ).fetchone()
    return row["c"]
