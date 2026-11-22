from src.core.database import init_db, get_db
from src.core.log_insert import insert_anomaly_log


def test_insert_anomaly_log_respeita_not_null():
    init_db()
    with get_db() as conn:
        insert_anomaly_log(
            conn,
            "ml_detector",
            "MultivariateAnomaly",
            {"timestamp": "2026-11-22T10:00:00+00:00", "score": 0.9},
        )
        conn.commit()
        row = conn.execute(
            "SELECT level, event_name FROM logs WHERE source = 'ml_detector'"
        ).fetchone()
    assert row["level"] == "WARNING"
    assert row["event_name"] == "MultivariateAnomaly"