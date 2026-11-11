from src.core.database import init_db, get_db
from src.core.detector import detect_volumetric_anomalies
from src.core.ml_detector import detect_multivariate_anomalies
from src.core.rules_engine import evaluate_cloudtrail_event

def run_sprint2_validation():
    print("--- A iniciar Validação da Sprint 2 (MAO-10) ---")
    
    # 1. Inicializar BD
    init_db()
    print("[OK] Base de dados verificada/inicializada.")
    
    # 2. Testar Detetor Volumétrico
    vol_anomalies = detect_volumetric_anomalies()
    print(f"[OK] Detetor Volumétrico executado. Anomalias: {len(vol_anomalies)}")
    
    # 3. Testar Detetor Multivariado
    ml_anomalies = detect_multivariate_anomalies()
    print(f"[OK] Detetor Multivariado executado. Anomalias: {len(ml_anomalies)}")
    
    # 4. Testar Motor de Regras CloudTrail
    test_event = {"eventName": "DeactivateMFADevice", "userIdentity": {"type": "IAMUser"}}
    alerts = evaluate_cloudtrail_event(test_event)
    print(f"[OK] Motor de Regras CloudTrail executado. Alertas gerados: {len(alerts)}")
    
    print("--- Validação da Sprint 2 concluída com sucesso! ---")

if __name__ == "__main__":
    run_sprint2_validation()
