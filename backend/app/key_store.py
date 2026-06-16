from __future__ import annotations

import base64
import json
import os
from pathlib import Path


def _current_login() -> str:
    """Return a stable login name for salting.

    ``os.getlogin()`` raises ``OSError`` when there is no controlling
    terminal (e.g. CI runners, daemons), so fall back to environment
    variables and finally a constant. The exact value only needs to be
    stable on a given machine, not globally unique.
    """
    try:
        name = os.getlogin()
        if name:
            return name
    except OSError:
        pass
    for var in ("USER", "USERNAME", "LOGNAME"):
        value = os.environ.get(var)
        if value:
            return value
    return "user"


class KeyStore:
    """Best-effort local secret storage.

    Uses the optional keyring package when available. If it is not installed,
    falls back to a user-local obfuscated JSON file so the API key is never
    stored in SQLite or returned by the API.
    """

    service = "skill-workbench"

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.path = data_dir / "secrets.json"
        self._keyring = self._load_keyring()

    def set(self, key: str, value: str) -> None:
        if self._keyring:
            self._keyring.set_password(self.service, key, value)
            return
        data = self._read_fallback()
        data[key] = self._encode(value)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get(self, key: str) -> str | None:
        if self._keyring:
            return self._keyring.get_password(self.service, key)
        data = self._read_fallback()
        encoded = data.get(key)
        return self._decode(encoded) if encoded else None

    def delete(self, key: str) -> None:
        if self._keyring:
            try:
                self._keyring.delete_password(self.service, key)
            except Exception:
                pass
            return
        data = self._read_fallback()
        data.pop(key, None)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _read_fallback(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _load_keyring():
        try:
            import keyring  # type: ignore

            return keyring
        except Exception:
            return None

    @staticmethod
    def _machine_salt() -> bytes:
        value = f"{_current_login()}:{os.name}".encode("utf-8", errors="ignore")
        return value or b"skill-workbench"

    def _encode(self, value: str) -> str:
        raw = value.encode("utf-8")
        salt = self._machine_salt()
        mixed = bytes(byte ^ salt[index % len(salt)] for index, byte in enumerate(raw))
        return base64.urlsafe_b64encode(mixed).decode("ascii")

    def _decode(self, value: str) -> str:
        mixed = base64.urlsafe_b64decode(value.encode("ascii"))
        salt = self._machine_salt()
        raw = bytes(byte ^ salt[index % len(salt)] for index, byte in enumerate(mixed))
        return raw.decode("utf-8")
