# yara_manager.py — полностью отключаем YARA, чтобы пока не падало

import logging

logger = logging.getLogger(__name__)

class YaraManager:
    """
    Заглушка YaraManager: у self.enabled всегда False,
    чтобы пропускать все YARA-вызовы без ошибок.
    """
    def __init__(self, rules_dir=None):
        self.enabled = False
        self.compiled_rules = {}

    def load_rules(self):
        logger.info("YARA disabled — load_rules skipped.")

    def scan(self, file_path: str):
        logger.info("YARA disabled — scan skipped.")
        return []

_default_mgr = YaraManager()

def scan_yara(file_path: str):
    """
    Возвращает пустой список — YARA отключена.
    """
    return []

def scan_yara_verbose(file_path: str):
    """
    Возвращает пустой список — YARA отключена.
    """
    return []
