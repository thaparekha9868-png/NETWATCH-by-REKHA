"""
detector.py
Anomaly detection for network metrics.

Two strategies are included:
  1. RollingStatsDetector  - simple, explainable, no training needed.
     Flags a point anomalous if it's more than `threshold` standard
     deviations from the recent rolling mean. Good baseline, good to
     explain in interviews.
  2. IsolationForestDetector - unsupervised ML model (scikit-learn).
     Learns the "shape" of normal traffic across all three features
     at once (latency, packet loss, bandwidth) and flags points that
     don't fit. Better at catching combined/subtle anomalies.

The Flask app uses IsolationForestDetector by default once enough
history exists, and falls back to RollingStatsDetector on cold start.
"""

import numpy as np
from sklearn.ensemble import IsolationForest

FEATURES = ["latency_ms", "packet_loss_pct", "bandwidth_mbps"]
MIN_TRAINING_POINTS = 30


class RollingStatsDetector:
    def __init__(self, threshold=3.0):
        self.threshold = threshold

    def score(self, history, point):
        """
        history: list of dicts (past metrics)
        point: dict (new metric to evaluate)
        Returns (is_anomaly: bool, score: float)
        """
        if len(history) < 5:
            return False, 0.0

        z_scores = []
        for feature in FEATURES:
            values = np.array([h[feature] for h in history])
            mean, std = values.mean(), values.std()
            if std == 0:
                continue
            z = abs(point[feature] - mean) / std
            z_scores.append(z)

        max_z = max(z_scores) if z_scores else 0.0
        return max_z > self.threshold, round(float(max_z), 3)


class IsolationForestDetector:
    def __init__(self, contamination=0.08):
        self.model = IsolationForest(
            n_estimators=150,
            contamination=contamination,
            random_state=42,
        )
        self.is_trained = False

    def fit(self, history):
        if len(history) < MIN_TRAINING_POINTS:
            return False
        X = np.array([[h[f] for f in FEATURES] for h in history])
        self.model.fit(X)
        self.is_trained = True
        return True

    def score(self, point):
        """Returns (is_anomaly: bool, score: float). Higher score = more anomalous."""
        if not self.is_trained:
            return False, 0.0
        X = np.array([[point[f] for f in FEATURES]])
        prediction = self.model.predict(X)[0]        # -1 = anomaly, 1 = normal
        raw_score = -self.model.score_samples(X)[0]  # higher = more anomalous
        return bool(prediction == -1), round(float(raw_score), 3)


class AnomalyEngine:
    """Wraps both strategies and picks the right one based on available history."""

    def __init__(self):
        self.rolling = RollingStatsDetector()
        self.iso_forest = IsolationForestDetector()

    def evaluate(self, history, point):
        if len(history) >= MIN_TRAINING_POINTS:
            if not self.iso_forest.is_trained or len(history) % 20 == 0:
                self.iso_forest.fit(history)  # periodically retrain on fresh history
            return self.iso_forest.score(point)
        return self.rolling.score(history, point)
