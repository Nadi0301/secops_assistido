from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.core.database import get_db, init_db
from src.core.detector import detect_volumetric_anomalies
from src.core.rules_engine import evaluate_cloudtrail_event

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="SecOps Assistido API", version="2.0", lifespan=lifespan)

class LogIngestRequest(BaseModel):
    source: str
    event_name: str
    details: dict

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
        ts = datetime.now(timezone.utc).isoformat()
        details = payload.details or {}
        level = str(details.get("level") or "INFO")
        message = str(
            details.get("message")
            or f"{payload.event_name} from {payload.source}"
        )
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO logs (timestamp, level, message, source, event_name, raw_data)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    ts,
                    level,
                    message,
                    payload.source,
                    payload.event_name,
                    json.dumps(details, ensure_ascii=False),
                ),
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
