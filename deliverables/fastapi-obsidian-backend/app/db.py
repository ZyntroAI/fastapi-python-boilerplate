"""Tiny JSON-file database with optional encryption at rest (Fernet/AES-128)."""
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

from .config import settings


class DB:
    def __init__(self):
        self._fernet = None

    def init(self, encrypt: bool = False):
        self._fernet = None
        if encrypt:
            self._fernet = Fernet(self._load_or_create_key())

    @property
    def encryption_active(self) -> bool:
        return self._fernet is not None

    def _load_or_create_key(self) -> bytes:
        key = os.environ.get(settings.encryption_key_env)
        if key:
            return key.encode()
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        keyfile = settings.data_dir / "secret.key"
        if keyfile.exists():
            return keyfile.read_bytes().strip()
        k = Fernet.generate_key()
        keyfile.write_bytes(k)
        return k

    def _store_path(self, name: str) -> Path:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        return settings.data_dir / f"{name}.json"

    def get(self, name: str, default=None):
        path = self._store_path(name)
        if not path.exists():
            return default
        raw = path.read_text(encoding="utf-8")
        if self._fernet is not None:
            raw = self._fernet.decrypt(raw.encode()).decode()
        return json.loads(raw)

    def set(self, name: str, value) -> None:
        raw = json.dumps(value, ensure_ascii=False)
        if self._fernet is not None:
            raw = self._fernet.encrypt(raw.encode()).decode()
        path = self._store_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(raw, encoding="utf-8")

    def close(self):
        self._fernet = None


db = DB()
