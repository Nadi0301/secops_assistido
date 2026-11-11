import sqlite3
from contextlib import contextmanager
import os

DB_PATH = "data/secops.db"

@contextmanager
def get_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                source TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,
                details TEXT,
                score REAL
            )
        ''')
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Base de dados e tabelas criadas com sucesso.")
