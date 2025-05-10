# hash_utils.py

import sqlite3
import hashlib
import logging
from pathlib import Path
from typing import Optional, Literal

logger = logging.getLogger(__name__)

class HashUtils:
    def __init__(self, db_path: str = "blackice.db"):
        self.db_path = Path(db_path)
        self.known_hashes = set()
        self._load_signatures()

    def _load_signatures(self):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cur = conn.execute("SELECT hash FROM signatures")
            self.known_hashes = {row[0] for row in cur}
            conn.close()
        except Exception as e:
            logger.error(f"Cannot load signatures from DB: {e}")
            self.known_hashes = set()

    @staticmethod
    def compute_hash(
        filepath: str,
        method: Literal["md5", "sha1", "sha256"] = "md5",
        chunk_size: int = 8192
    ) -> Optional[str]:
        algo = method.lower()
        if algo == "md5":
            h = hashlib.md5()
        elif algo == "sha1":
            h = hashlib.sha1()
        elif algo == "sha256":
            h = hashlib.sha256()
        else:
            raise ValueError(f"Unsupported hash method: {method}")

        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception as e:
            logger.warning(f"Hash compute failed for {filepath}: {e}")
            return None

    def is_known(self, hexdigest: str) -> bool:
        if not hexdigest:
            return False
        return hexdigest.lower() in self.known_hashes

    def reload_signatures(self):
        """Перезагрузить сигнатуры из БД заново."""
        self._load_signatures()
