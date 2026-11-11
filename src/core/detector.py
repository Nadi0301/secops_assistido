import statistics
from src.core.database import get_db

def detect_volumetric_anomalies(threshold_multiplier=2.0):
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                   COUNT(*) as count
            FROM logs
            GROUP BY hour
        """)
        rows = cursor.fetchall()
        
        if not rows:
            return []
            
        counts = [row['count'] for row in rows]
        if len(counts) < 3:
            return []
            
        mean = statistics.mean(counts)
        stdev = statistics.stdev(counts) if len(counts) > 1 else 0
        
        anomalies = []
        for row in rows:
            if stdev > 0 and (row['count'] - mean) > (threshold_multiplier * stdev):
                anomalies.append({
                    'timestamp': row['hour'],
                    'anomaly_type': 'volumetric_spike',
                    'details': f"Volume de logs ({row['count']}) acima da média ({mean:.2f})",
                    'score': float((row['count'] - mean) / stdev)
                })
        return anomalies

if __name__ == "__main__":
    anomalias = detect_volumetric_anomalies()
    print(f"Detecção concluída. Anomalias encontradas: {len(anomalias)}")
