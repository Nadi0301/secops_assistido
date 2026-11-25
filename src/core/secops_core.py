import json
from pathlib import Path
from src.core.log_insert import insert_anomaly_log
from src.core.database import get_db, init_db
from src.core.detector import detect_volumetric_anomalies
from src.core.ml_detector import detect_multivariate_anomalies
from src.core.rules_engine import evaluate_cloudtrail_event
from secops_core.config import get_settings


def _load_candidate_events(vol_anomalies, ml_anomalies):
    events = []
    logs_path = Path(get_settings().logs_jsonl_path)
    if logs_path.exists():
        for line in logs_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
                if isinstance(parsed, dict):
                    events.append(parsed)
            except json.JSONDecodeError:
                continue
    if events:
        return events
    for source in (vol_anomalies or [], ml_anomalies or []):
        if isinstance(source, list):
            for item in source:
                if isinstance(item, dict):
                    events.append(item)
    return events


def run_unified_pipeline():
    init_db()
    results = {
        "volumetric_anomalies": [],
        "multivariate_anomalies": [],
        "cloudtrail_alerts": []
    }

    # 1. Executar detetor volumetrico
    vol_anomalies = detect_volumetric_anomalies()
    results["volumetric_anomalies"] = vol_anomalies

    # 2. Executar detetor multivariado
    ml_anomalies = detect_multivariate_anomalies()
    results["multivariate_anomalies"] = ml_anomalies

    # 3. Avaliar regras deterministicas CloudTrail
    cloudtrail_alerts = []
    for event_data in _load_candidate_events(vol_anomalies, ml_anomalies):
        triggered = evaluate_cloudtrail_event(event_data)
        for rule_hit in triggered:
            alert_record = dict(rule_hit)
            if event_data.get("eventName"):
                alert_record["eventName"] = event_data.get("eventName")
            if event_data.get("eventID"):
                alert_record["eventID"] = event_data.get("eventID")
            cloudtrail_alerts.append(alert_record)
    results["cloudtrail_alerts"] = cloudtrail_alerts

    # 4. Persistir resultados na base de dados
    with get_db() as conn:
        for anom in vol_anomalies:
            insert_anomaly_log(conn, "volumetric_detector", "VolumetricAnomaly", anom)
        for anom in ml_anomalies:
            insert_anomaly_log(conn, "ml_detector", "MultivariateAnomaly", anom)
        for alert in cloudtrail_alerts:
            insert_anomaly_log(conn, "rules_engine", "CloudTrailRuleAlert", alert)
        conn.commit()

    return results


if __name__ == "__main__":
    res = run_unified_pipeline()
    print("[Pipeline Hibrido] Executado com sucesso:", res)
