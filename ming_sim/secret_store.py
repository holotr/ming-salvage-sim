"""Encrypted secret storage helpers for the web fork.

The web app stores user supplied API keys encrypted at rest.  The master key is
kept outside the database in ``MING_SIM_SECRET_KEY`` so database backups alone
are not enough to recover secrets.
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SecretStoreError(RuntimeError):
    """Raised when encrypted secrets cannot be read or written."""


def generate_master_key() -> str:
    """Return a new urlsafe base64 encoded 32-byte key."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode("ascii")


def _decode_master_key(value: str) -> bytes:
    raw = (value or "").strip()
    if not raw:
        raise SecretStoreError("未配置 MING_SIM_SECRET_KEY，无法加密保存 API Key。")
    if len(raw) == 64:
        try:
            key = bytes.fromhex(raw)
            if len(key) == 32:
                return key
        except ValueError:
            pass
    padded = raw + ("=" * (-len(raw) % 4))
    try:
        key = base64.urlsafe_b64decode(padded.encode("ascii"))
    except Exception as exc:  # noqa: BLE001
        raise SecretStoreError("MING_SIM_SECRET_KEY 必须是 32 字节的 base64 或 hex 字符串。") from exc
    if len(key) != 32:
        raise SecretStoreError("MING_SIM_SECRET_KEY 解码后必须正好 32 字节。")
    return key


@dataclass(frozen=True)
class SecretStore:
    key: bytes

    @classmethod
    def from_env(cls) -> "SecretStore":
        return cls(_decode_master_key(os.environ.get("MING_SIM_SECRET_KEY", "")))

    def encrypt(self, plaintext: str) -> str:
        text = (plaintext or "").strip()
        if not text:
            return ""
        nonce = os.urandom(12)
        ciphertext = AESGCM(self.key).encrypt(nonce, text.encode("utf-8"), b"ming-sim-api-key")
        return "v1:" + base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")

    def decrypt(self, token: str) -> str:
        data = (token or "").strip()
        if not data:
            return ""
        if not data.startswith("v1:"):
            raise SecretStoreError("密钥密文格式不受支持。")
        try:
            packed = base64.urlsafe_b64decode(data[3:].encode("ascii"))
            nonce, ciphertext = packed[:12], packed[12:]
            return AESGCM(self.key).decrypt(nonce, ciphertext, b"ming-sim-api-key").decode("utf-8")
        except Exception as exc:  # noqa: BLE001
            raise SecretStoreError("无法解密 API Key，请检查 MING_SIM_SECRET_KEY 是否匹配。") from exc
