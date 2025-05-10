import os
import asyncio
from PySide6.QtCore import QThread, Signal

from hash_utils import HashUtils
from vt_api import VirusTotalAPI

def list_files(root: str) -> list[str]:
    files = []
    if os.path.isdir(root):
        for dp, _, names in os.walk(root):
            for fn in names:
                files.append(os.path.join(dp, fn))
    else:
        files = [root]
    return files

class ScanWorker(QThread):
    progress     = Signal(int)
    file_scanned = Signal(str, str)
    log          = Signal(str)
    finished     = Signal()

    def __init__(self, target_path: str, vt_api_key: str = None):
        super().__init__()
        self.target_path = target_path
        self._running    = True
        self.hash_utils  = HashUtils()
        # VirusTotalAPI теперь принимает ключ по имени api_key
        self.vt_api      = VirusTotalAPI(api_key=vt_api_key)

    def stop(self):
        self._running = False

    def run(self):
        files = list_files(self.target_path)
        total = len(files)
        for i, fpath in enumerate(files, 1):
            if not self._running:
                break
            self.log.emit(f"Scanning: {fpath}")
            try:
                # 1) Hashes
                hashes = {
                    algo: self.hash_utils.compute_hash(fpath, algo)
                    for algo in ("md5", "sha1", "sha256")
                }
                if any(self.hash_utils.is_known(h or "") for h in hashes.values()):
                    level, detail = "High", "Known malicious hash"
                else:
                    # 2) YARA (отключите/заглушите при необходимости)
                    hits = []
                    level, detail = ("Medium", f"YARA: {', '.join(hits)}") if hits else (None, None)
                    if level is None:
                        # 3) VirusTotal
                        key = hashes.get("sha256") or hashes.get("md5") or ""
                        vt = asyncio.run(self.vt_api.check_file(key))
                        stats = (
                            vt.get("data", {})
                              .get("attributes", {})
                              .get("last_analysis_stats", {})
                        ) if vt else {}
                        if stats.get("malicious", 0) > 0:
                            level, detail = "High", "VT malicious"
                        elif stats.get("suspicious", 0) > 0:
                            level, detail = "Medium", "VT suspicious"
                        else:
                            level, detail = "Clean", "No threats"

                self.file_scanned.emit(fpath, level)
                self.log.emit(detail)
            except Exception as e:
                self.log.emit(f"Error: {e}")
                self.file_scanned.emit(fpath, "Unknown")

            self.progress.emit(int(i / total * 100))
        self.finished.emit()
