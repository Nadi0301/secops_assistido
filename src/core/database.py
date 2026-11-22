from contextlib import contextmanager
import os
import sqlite3

DB_PATH = os.environ.get("SECOPS_SRC_DB_PATH", "data/secops.db")


def _resolve_db_path() -> str:
    return os.environ.get("SECOPS_SRC_DB_PATH", DB_PATH)


@contextmanager
def get_db():
    db_file = _resolve_db_path()
    parent_dir = os.path.dirname(db_file)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                source TEXT,
                event_name TEXT,
                raw_data TEXT
            )
            """
        )
        existing_cols = {
            row["name"] for row in conn.execute("PRAGMA table_info(logs)").fetchall()
        }
        if "event_name" not in existing_cols:
            conn.execute("ALTER TABLE logs ADD COLUMN event_name TEXT")
        if "raw_data" not in existing_cols:
            conn.execute("ALTER TABLE logs ADD COLUMN raw_data TEXT")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,
                details TEXT,
                score REAL
            )
            """
        )
        conn.commit()


if __name__ == "__main__":
    init_db()
    print("Base de dados e tabelas criadas com sucesso.")
