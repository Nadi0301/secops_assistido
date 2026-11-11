from src.core.database import get_db, init_db
from src.core.detector import detect_volumetric_anomalies
from src.core.ml_detector import detect_multivariate_anomalies
from src.core.rules_engine import evaluate_cloudtrail_event

def run_unified_pipeline():
    init_db()
    results = {
        "volumetric_anomalies": [],
        "multivariate_anomalies": [],
        "cloudtrail_alerts": []
    }

    # 1. Executar detetor volumétrico
    vol_anomalies = detect_volumetric_anomalies()
    results["volumetric_anomalies"] = vol_anomalies

    # 2. Executar detetor multivariado
    ml_anomalies = detect_multivariate_anomalies()
    results["multivariate_anomalies"] = ml_anomalies

    # 3. Persistir resultados na base de dados
    with get_db() as conn:
        for anom in vol_anomalies:
            conn.execute(
                "INSERT INTO logs (source, event_name, raw_data) VALUES (?, ?, ?)",
                ("volumetric_detector", "VolumetricAnomaly", str(anom))
            )
        for anom in ml_anomalies:
            conn.execute(
                "INSERT INTO logs (source, event_name, raw_data) VALUES (?, ?, ?)",
                ("ml_detector", "MultivariateAnomaly", str(anom))
            )
        conn.commit()

    return results

if __name__ == "__main__":
    res = run_unified_pipeline()
    print("[Pipeline Híbrido] Executado com sucesso:", res)
