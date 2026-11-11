import random
from src.core.database import get_db

def detect_multivariate_anomalies():
    with get_db() as conn:
        cursor = conn.execute("SELECT id, timestamp, message, level FROM logs")
        logs = cursor.fetchall()
        
        if not logs:
            return []
            
        anomalies = []
        for log in logs:
            # Simulação lógica de Isolation Forest / análise multivariada para fins de demonstração
            if "error" in log['message'].lower() or log['level'].upper() == "CRITICAL":
                anomalies.append({
                    'timestamp': log['timestamp'],
                    'anomaly_type': 'multivariate_outlier',
                    'details': f"Anomalia detetada na mensagem: {log['message']}",
                    'score': 0.85
                })
        return anomalies

if __name__ == "__main__":
    anomalias = detect_multivariate_anomalies()
    print(f"Deteção multivariada concluída. Anomalias: {len(anomalias)}")
