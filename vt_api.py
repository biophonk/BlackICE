import os
import logging
from typing import Optional, Dict, Any

import requests

from cache import DiskCache

logger = logging.getLogger(__name__)

class VirusTotalAPI:
    def __init__(self,
                 api_key: Optional[str]=None,
                 cache_dir: str="cache",
                 cache_ttl: Optional[int]=None):
        self.api_key = api_key or os.getenv("VIRUSTOTAL_API_KEY")
        if not self.api_key:
            raise ValueError("VT API key is not set")
        self.base_url = "https://www.virustotal.com/api/v3/files/{hash}"
        self.cache    = DiskCache(cache_dir=cache_dir, ttl=cache_ttl)
        self.session  = requests.Session()
        self.session.headers.update({"x-apikey": self.api_key})
        self._mem_cache: Dict[str, Any] = {}

    def check_file(self, hexdigest: str) -> Optional[Dict[str, Any]]:
        if hexdigest in self._mem_cache:
            return self._mem_cache[hexdigest]
        cached = self.cache.get(hexdigest)
        if cached is not None:
            self._mem_cache[hexdigest] = cached
            return cached
        try:
            resp = self.session.get(self.base_url.format(hash=hexdigest), timeout=15)
        except requests.RequestException as e:
            logger.error(f"VT request failed: {e}")
            return None
        if resp.status_code == 200:
            try:
                data = resp.json()
                self.cache.set(hexdigest, data)
                self._mem_cache[hexdigest] = data
                return data
            except ValueError as e:
                logger.error(f"VT JSON parse failed: {e}")
        else:
            logger.warning(f"VT API status {resp.status_code}: {resp.text}")
        return None

    def invalidate(self, hexdigest: str):
        self._mem_cache.pop(hexdigest, None)
        self.cache.invalidate(hexdigest)

    def clear_cache(self):
        self._mem_cache.clear()
        self.cache.clear()
