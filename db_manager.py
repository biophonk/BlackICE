import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from threading import Lock

class DatabaseManager:
    """
    Менеджер БД для BlackICE.
    Поддерживает сканы, алерты, логи и хранение сигнатур.
    """
    _SCHEMA = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS signatures (
        hash TEXT PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS scans (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        path        TEXT    NOT NULL,
        start_time  TEXT    NOT NULL,
        end_time    TEXT,
        result      TEXT
    );

    CREATE TABLE IF NOT EXISTS alerts (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id   INTEGER NOT NULL,
        path      TEXT    NOT NULL,
        level     TEXT    NOT NULL,
        detail    TEXT,
        FOREIGN KEY(scan_id) REFERENCES scans(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp  TEXT    NOT NULL,
        message    TEXT    NOT NULL
    );
    """

    _INDEXES = """
    CREATE INDEX IF NOT EXISTS idx_scans_start_time ON scans(start_time);
    CREATE INDEX IF NOT EXISTS idx_logs_timestamp    ON logs(timestamp);
    """

    def __init__(self, db_path: str = "blackice.db"):
        self._lock   = Lock()
        self.db_file = Path(db_path)
        first        = not self.db_file.exists()
        self.conn    = sqlite3.connect(str(self.db_file), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        if first:
            with self.conn:
                self.conn.executescript(self._SCHEMA)
                self.conn.executescript(self._INDEXES)

    def close(self):
        with self._lock:
            if self.conn:
                self.conn.close()
                self.conn = None

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat(sep=" ", timespec="seconds")

    def start_scan(self, path: str) -> int:
        ts = self._now()
        with self._lock, self.conn:
            cur = self.conn.execute(
                "INSERT INTO scans(path, start_time) VALUES (?, ?)",
                (path, ts)
            )
            return cur.lastrowid

    def finish_scan(self, scan_id: int, result: str = None):
        ts = self._now()
        if result is not None:
            sql    = "UPDATE scans SET end_time = ?, result = ? WHERE id = ?"
            params = (ts, result, scan_id)
        else:
            sql    = "UPDATE scans SET end_time = ? WHERE id = ?"
            params = (ts, scan_id)
        with self._lock, self.conn:
            self.conn.execute(sql, params)

    def add_scan(self, path: str, result: str) -> int:
        sid = self.start_scan(path)
        self.finish_scan(sid, result)
        return sid

    def add_alert(self, scan_id: int, path: str, level: str, detail: str = ""):
        with self._lock, self.conn:
            self.conn.execute(
                "INSERT INTO alerts(scan_id, path, level, detail) VALUES (?, ?, ?, ?)",
                (scan_id, path, level, detail)
            )

    def add_log(self, message: str):
        ts = self._now()
        with self._lock, self.conn:
            self.conn.execute(
                "INSERT INTO logs(timestamp, message) VALUES (?, ?)",
                (ts, message)
            )

    def get_scan_logs(self):
        """
        Возвращает список последних сканов:
        Row[id, path, start_time, end_time, result]
        """
        with self._lock:
            cur = self.conn.execute(
                "SELECT id, path, start_time, result FROM scans ORDER BY start_time DESC"
            )
            return [dict(row) for row in cur.fetchall()]

    def get_alerts(self, scan_id: int = None):
        if scan_id is None:
            cur = self.conn.execute(
                "SELECT scan_id, path, level, detail FROM alerts ORDER BY id DESC"
            )
        else:
            cur = self.conn.execute(
                "SELECT path, level, detail FROM alerts WHERE scan_id = ? ORDER BY id",
                (scan_id,)
            )
        return cur.fetchall()

    def get_logs(self):
        cur = self.conn.execute("SELECT timestamp, message FROM logs ORDER BY id DESC")
        return cur.fetchall()

    def purge_logs_older_than(self, days: int):
        cutoff     = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff.isoformat(sep=" ", timespec="seconds")
        with self._lock, self.conn:
            self.conn.execute(
                "DELETE FROM logs WHERE timestamp <= ?", (cutoff_str,)
            )
