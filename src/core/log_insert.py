import json
from datetime import datetime, timezone


def insert_anomaly_log(conn, source, event_name, anom):
    ts = None
    if isinstance(anom, dict):
        ts = anom.get("timestamp")
    ts = ts or datetime.now(timezone.utc).isoformat()
    message = f"{event_name} detectado por {source}"
    conn.execute(
        """
        INSERT INTO logs (timestamp, level, message, source, event_name, raw_data)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            ts,
            "WARNING",
            message,
            source,
            event_name,
            json.dumps(anom, ensure_ascii=False, default=str),
        ),
    )