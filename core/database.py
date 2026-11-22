import os
import sqlite3

class StateDB:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            app_data = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ClutterSweep")
            os.makedirs(app_data, exist_ok=True)
            db_path = os.path.join(app_data, "sweep_state.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
        
    def _init_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS file_states (
                    path TEXT PRIMARY KEY,
                    size INTEGER,
                    status TEXT CHECK(status IN ('UNVISITED', 'VISITED', 'DELETED')) DEFAULT 'UNVISITED'
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    key TEXT PRIMARY KEY,
                    value INTEGER DEFAULT 0
                )
            """)
            self.conn.execute(
                "INSERT OR IGNORE INTO metrics (key, value) VALUES ('bytes_freed', 0)"
            )

    def get_status(self, path: str) -> str:
        cur = self.conn.execute("SELECT status FROM file_states WHERE path = ?", (path,))
        row = cur.fetchone()
        return row[0] if row else "UNVISITED"

    def set_status(self, path: str, size: int, status: str):
        with self.conn:
            self.conn.execute("""
                INSERT INTO file_states (path, size, status)
                VALUES (?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET status = excluded.status
            """, (path, size, status))
            if status == "DELETED":
                self.conn.execute(
                    "UPDATE metrics SET value = value + ? WHERE key = 'bytes_freed'", (size,)
                )

    def get_all_states(self) -> dict[str, str]:
        cur = self.conn.execute("SELECT path, status FROM file_states")
        return dict(cur.fetchall())

    def get_bytes_freed(self) -> int:
        cur = self.conn.execute("SELECT value FROM metrics WHERE key = 'bytes_freed'")
        return cur.fetchone()[0]