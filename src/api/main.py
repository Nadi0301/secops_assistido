from fastapi import FastAPI, HTTPException
from src.core.database import get_db
from src.core.detector import detect_volumetric_anomalies
from src.core.rules_engine import evaluate_cloudtrail_event

app = FastAPI(title="SecOps Assistido API", version="2.0")

@app.get("/")
def read_root():
    return {"status": "online", "project": "SecOps Assistido v2"}

@app.get("/logs")
def get_logs(limit: int = 50):
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

@app.get("/anomalies/detect")
def run_detection():
    anomalies = detect_volumetric_anomalies()
    return {"anomalies_detected": len(anomalies), "items": anomalies}

@app.post("/rules/evaluate")
def evaluate_rule(event: dict):
    alerts = evaluate_cloudtrail_event(event)
    return {"alerts": alerts}
