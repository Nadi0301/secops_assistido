from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.core.database import get_db, init_db
from src.core.detector import detect_volumetric_anomalies
from src.core.rules_engine import evaluate_cloudtrail_event

app = FastAPI(title="SecOps Assistido API", version="2.0")

class LogIngestRequest(BaseModel):
    source: str
    event_name: str
    details: dict

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"status": "online", "project": "SecOps Assistido v2"}

@app.get("/logs")
def get_logs(limit: int = 50):
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

@app.post("/pipeline/trigger")
def trigger_pipeline(payload: LogIngestRequest):
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO logs (source, event_name, raw_data) VALUES (?, ?, ?)",
                (payload.source, payload.event_name, str(payload.details))
            )
            conn.commit()
        
        # Executar verificações de anomalias e regras sobre o evento inserido
        vol_anomalies = detect_volumetric_anomalies()
        alerts = evaluate_cloudtrail_event({"eventName": payload.event_name, "details": payload.details})

        return {
            "status": "success",
            "message": "Pipeline executado sob demanda com sucesso.",
            "volumetric_anomalies_found": len(vol_anomalies),
            "rules_alerts_triggered": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
