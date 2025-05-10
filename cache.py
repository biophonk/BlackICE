import json
import logging
from pathlib import Path
from threading import RLock
from time import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DiskCache:
    def __init__(self, cache_dir: str = "cache", ttl: Optional[int] = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl       = ttl
        self._lock     = RLock()

    def _safe_filename(self, key: str) -> str:
        return "".join(c for c in key if c.isalnum() or c in "-_") or "cache"

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{self._safe_filename(key)}.json"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        path = self._path(key)
        with self._lock:
            if not path.exists():
                return None
            if self.ttl is not None and time() - path.stat().st_mtime > self.ttl:
                path.unlink(missing_ok=True)
                return None
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"DiskCache.get failed: {e}")
                return None

    def set(self, key: str, data: Dict[str, Any]) -> None:
        path = self._path(key)
        tmp  = path.with_suffix(".json.tmp")
        with self._lock:
            try:
                tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
                tmp.replace(path)
            except Exception as e:
                logger.error(f"DiskCache.set failed: {e}")

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._path(key).unlink(missing_ok=True)

    def clear(self) -> None:
        with self._lock:
            for file in self.cache_dir.glob("*.json"):
                file.unlink(missing_ok=True)
