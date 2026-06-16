import os

import app.key_store as key_store_module
from app.key_store import KeyStore


def test_set_and_get_roundtrip_via_fallback(tmp_path, monkeypatch):
    # 强制走文件回退路径(无 keyring),验证加解密对称
    monkeypatch.setattr(KeyStore, "_load_keyring", staticmethod(lambda: None))
    store = KeyStore(tmp_path)

    store.set("SKILL_WORKBENCH_API_KEY", "secret-value")

    # 明文不应直接出现在落盘文件里
    raw = (tmp_path / "secrets.json").read_text(encoding="utf-8")
    assert "secret-value" not in raw
    assert store.get("SKILL_WORKBENCH_API_KEY") == "secret-value"

    store.delete("SKILL_WORKBENCH_API_KEY")
    assert store.get("SKILL_WORKBENCH_API_KEY") is None


def test_salt_survives_getlogin_oserror(monkeypatch):
    # CI runner / 守护进程没有控制终端时 os.getlogin() 会抛
    # OSError: [Errno 25] Inappropriate ioctl for device。
    def _raise(*_args, **_kwargs):
        raise OSError(25, "Inappropriate ioctl for device")

    monkeypatch.setattr(key_store_module.os, "getlogin", _raise)
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.delenv("USERNAME", raising=False)
    monkeypatch.delenv("LOGNAME", raising=False)

    salt = KeyStore._machine_salt()

    assert isinstance(salt, bytes)
    assert salt  # 不为空，确保后续异或不会除零/越界


def test_encode_decode_roundtrip_without_tty(monkeypatch, tmp_path):
    def _raise(*_args, **_kwargs):
        raise OSError(25, "Inappropriate ioctl for device")

    monkeypatch.setattr(key_store_module.os, "getlogin", _raise)
    monkeypatch.setattr(KeyStore, "_load_keyring", staticmethod(lambda: None))
    store = KeyStore(tmp_path)

    store.set("k", "value-123")
    assert store.get("k") == "value-123"
