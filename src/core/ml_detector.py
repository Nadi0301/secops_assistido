from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from src.core.database import get_db

LEVEL_WEIGHT = {
    "DEBUG": 0.0,
    "INFO": 1.0,
    "WARNING": 2.0,
    "WARN": 2.0,
    "ERROR": 3.0,
    "CRITICAL": 4.0,
}


def _parse_hour(ts_value: str) -> float:
    if not ts_value:
        return 12.0
    try:
        dt = datetime.fromisoformat(str(ts_value).replace("Z", "+00:00"))
        return float(dt.hour)
    except ValueError:
        return 12.0


def _extract_features(log_row) -> list[float]:
    level = str(log_row["level"] or "").upper()
    message = str(log_row["message"] or "")
    ts = str(log_row["timestamp"] or "")

    level_score = LEVEL_WEIGHT.get(level, 1.0)
    msg_len = float(len(message))
    error_tokens = float(
        sum(
            token in message.lower()
            for token in ("error", "fail", "denied", "unauthorized", "timeout", "exception", "critical")
        )
    )
    hour_val = _parse_hour(ts)
    return [level_score, msg_len, error_tokens, hour_val]


def detect_multivariate_anomalies():
    with get_db() as conn:
        cursor = conn.execute("SELECT id, timestamp, message, level FROM logs")
        logs = cursor.fetchall()

    if not logs:
        return []

    if len(logs) < 5:
        anomalies = []
        for log in logs:
            if "error" in str(log["message"] or "").lower() or str(log["level"] or "").upper() == "CRITICAL":
                anomalies.append(
                    {
                        "timestamp": log["timestamp"],
                        "anomaly_type": "multivariate_outlier",
                        "details": f"Anomalia detetada na mensagem: {log['message']}",
                        "score": 0.85,
                    }
                )
        return anomalies

    features = np.array([_extract_features(row) for row in logs], dtype=float)
    model = IsolationForest(contamination="auto", random_state=42)
    preds = model.fit_predict(features)
    raw_scores = model.decision_function(features)

    min_s = float(np.min(raw_scores))
    max_s = float(np.max(raw_scores))
    span = max(max_s - min_s, 1e-9)

    anomalies = []
    for row, pred, s in zip(logs, preds, raw_scores):
        if pred == -1:
            normalized_score = round(min(1.0, max(0.0, (max_s - float(s)) / span)), 4)
            anomalies.append(
                {
                    "timestamp": row["timestamp"],
                    "anomaly_type": "multivariate_outlier",
                    "details": f"Anomalia multivariada (IsolationForest) detetada na mensagem: {row['message']}",
                    "score": max(normalized_score, 0.5),
                }
            )

    return anomalies


if __name__ == "__main__":
    anomalias = detect_multivariate_anomalies()
    print(f"Deteção multivariada concluída. Anomalias: {len(anomalias)}")
