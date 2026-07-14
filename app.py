"""
app.py
Flask entrypoint for the Network Anomaly Detection dashboard.

Run with:
    python app.py

Then open http://localhost:8000
"""

import os
import threading
import time

from flask import Flask, jsonify, render_template

from core import database, simulator
from core.detector import AnomalyEngine

app = Flask(__name__)
engine = AnomalyEngine()

SIMULATION_INTERVAL_SECONDS = 3
HISTORY_WINDOW_FOR_DETECTION = 200
_background_thread_started = False


def background_data_loop():
    """Continuously generates new metrics and scores them for anomalies."""
    while True:
        history = database.get_recent_metrics(limit=HISTORY_WINDOW_FOR_DETECTION)
        point = simulator.generate_point()
        is_anomaly, score = engine.evaluate(history, point)

        database.insert_metric(
            latency_ms=point["latency_ms"],
            packet_loss_pct=point["packet_loss_pct"],
            bandwidth_mbps=point["bandwidth_mbps"],
            is_anomaly=int(is_anomaly),
            anomaly_score=score,
        )
        time.sleep(SIMULATION_INTERVAL_SECONDS)


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/metrics")
def api_metrics():
    limit = 100
    metrics = database.get_recent_metrics(limit=limit)
    return jsonify({
        "metrics": metrics,
        "anomaly_count": database.get_anomaly_count(),
    })


@app.route("/api/seed", methods=["POST"])
def api_seed():
    """Backfill some historical data on first run so the dashboard isn't empty."""
    existing = database.get_recent_metrics(limit=1)
    if existing:
        return jsonify({"status": "already_seeded"})

    history = []
    for point in simulator.generate_batch(60):
        is_anomaly, score = engine.evaluate(history, point)
        database.insert_metric(
            latency_ms=point["latency_ms"],
            packet_loss_pct=point["packet_loss_pct"],
            bandwidth_mbps=point["bandwidth_mbps"],
            is_anomaly=int(is_anomaly),
            anomaly_score=score,
        )
        history.append(point)
    return jsonify({"status": "seeded", "count": 60})


def start_background_thread():
    """Initializes the DB and starts the simulator thread exactly once,
    whether the app is run directly (python app.py) or via gunicorn."""
    global _background_thread_started
    if _background_thread_started:
        return
    database.init_db()
    thread = threading.Thread(target=background_data_loop, daemon=True)
    thread.start()
    _background_thread_started = True


# Runs at import time so it works under gunicorn too, not just "python app.py"
start_background_thread()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=False, host="0.0.0.0", port=port)
