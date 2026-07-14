"""
simulator.py
Generates synthetic network telemetry (latency, packet loss, bandwidth).

In a real deployment you would swap this out for actual data collection,
e.g. pinging hosts, polling SNMP/UISP, or reading router logs. Simulation
lets you demo and test the anomaly detector without needing live infra.
"""

import random

BASE_LATENCY = 25.0       # ms
BASE_PACKET_LOSS = 0.5    # %
BASE_BANDWIDTH = 100.0    # mbps

ANOMALY_PROBABILITY = 0.08  # ~8% of points are anomalous, for demo purposes


def generate_point(force_anomaly=None):
    """
    Returns a dict of one simulated network measurement.
    force_anomaly: True/False to override random anomaly injection, or None for random.
    """
    is_injected_anomaly = (
        force_anomaly if force_anomaly is not None
        else random.random() < ANOMALY_PROBABILITY
    )

    if is_injected_anomaly:
        anomaly_type = random.choice(["latency_spike", "packet_loss_spike", "bandwidth_drop"])
        latency = BASE_LATENCY + random.uniform(150, 400) if anomaly_type == "latency_spike" else BASE_LATENCY + random.uniform(-5, 5)
        packet_loss = BASE_PACKET_LOSS + random.uniform(10, 30) if anomaly_type == "packet_loss_spike" else BASE_PACKET_LOSS + random.uniform(-0.3, 0.3)
        bandwidth = max(1.0, BASE_BANDWIDTH - random.uniform(60, 90)) if anomaly_type == "bandwidth_drop" else BASE_BANDWIDTH + random.uniform(-10, 10)
    else:
        latency = BASE_LATENCY + random.uniform(-5, 5)
        packet_loss = max(0.0, BASE_PACKET_LOSS + random.uniform(-0.3, 0.3))
        bandwidth = BASE_BANDWIDTH + random.uniform(-10, 10)

    return {
        "latency_ms": round(latency, 2),
        "packet_loss_pct": round(packet_loss, 2),
        "bandwidth_mbps": round(bandwidth, 2),
        "_injected_anomaly": is_injected_anomaly,  # ground truth, not stored in DB
    }


def generate_batch(n=50):
    return [generate_point() for _ in range(n)]
