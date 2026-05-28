"""Web authentication, sessions, and per-user LLM config storage."""

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from ming_sim.llm_config import normalize_openai_base_url
from ming_sim.models import LLMConfig
from ming_sim.paths import user_data_path
from ming_sim.secret_store import SecretStore

SESSION_DAYS_DEFAULT = 7
DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_MAX_TOKENS = 8000


@dataclass(frozen=True)
class AuthUser:
    id: int
    username: str
    role: str
    status: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


@dataclass(frozen=True)
class SessionTokens:
    token: str
    csrf_token: str
    expires_at: int


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthStore:
    """Small SQLite auth database kept separate from gameplay databases."""

    def __init__(self, path: str = "") -> None:
        self.path = path or os.environ.get("MING_SIM_AUTH_DB", "") or user_data_path("app_auth.db")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._ph = PasswordHasher()
        self.init_schema()

    def init_schema(self) -> None:
        with self._lock:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    last_login_at INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token_hash TEXT NOT NULL UNIQUE,
                    csrf_hash TEXT NOT NULL,
                    expires_at INTEGER NOT NULL,
                    created_at INTEGER NOT NULL,
                    last_seen_at INTEGER NOT NULL,
                    revoked_at INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                CREATE INDEX IF NOT EXISTS idx_sessions_user
                    ON sessions(user_id, revoked_at, expires_at);

                CREATE TABLE IF NOT EXISTS user_llm_configs (
                    user_id INTEGER PRIMARY KEY,
                    base_url TEXT NOT NULL,
                    model TEXT NOT NULL,
                    max_tokens INTEGER NOT NULL DEFAULT 8000,
                    advanced_model TEXT NOT NULL DEFAULT '',
                    advanced_base_url TEXT NOT NULL DEFAULT '',
                    encrypted_api_key TEXT NOT NULL DEFAULT '',
                    encrypted_advanced_api_key TEXT NOT NULL DEFAULT '',
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                """
            )
            self.conn.commit()

    def has_users(self) -> bool:
        with self._lock:
            row = self.conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
            return row is not None

    def list_users(self) -> List[Dict[str, object]]:
        with self._lock:
            rows = self.conn.execute(
                """
                SELECT id, username, role, status, created_at, updated_at, last_login_at
                FROM users
                ORDER BY id
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def get_user(self, user_id: int) -> Optional[AuthUser]:
        with self._lock:
            row = self.conn.execute(
                "SELECT id, username, role, status FROM users WHERE id = ?",
                (int(user_id),),
            ).fetchone()
        return self._row_to_user(row)

    def get_user_by_username(self, username: str) -> Optional[AuthUser]:
        with self._lock:
            row = self.conn.execute(
                "SELECT id, username, role, status FROM users WHERE username = ?",
                (self._clean_username(username),),
            ).fetchone()
        return self._row_to_user(row)

    def create_user(self, username: str, password: str, role: str = "user") -> AuthUser:
        name = self._clean_username(username)
        password = password or ""
        role = role if role in ("admin", "user") else "user"
        if len(name) < 3:
            raise ValueError("用户名至少 3 个字符。")
        if len(password) < 8:
            raise ValueError("密码至少 8 个字符。")
        now = int(time.time())
        password_hash = self._ph.hash(password)
        with self._lock:
            try:
                cur = self.conn.execute(
                    """
                    INSERT INTO users (username, password_hash, role, status, created_at, updated_at)
                    VALUES (?, ?, ?, 'active', ?, ?)
                    """,
                    (name, password_hash, role, now, now),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("用户名已存在。") from exc
            self.conn.commit()
            user_id = int(cur.lastrowid)
        user = self.get_user(user_id)
        if user is None:
            raise RuntimeError("创建用户失败。")
        return user

    def update_user(
        self,
        user_id: int,
        *,
        role: Optional[str] = None,
        status: Optional[str] = None,
        password: Optional[str] = None,
    ) -> AuthUser:
        updates: List[str] = []
        values: List[object] = []
        if role is not None:
            if role not in ("admin", "user"):
                raise ValueError("role 必须是 admin 或 user。")
            updates.append("role = ?")
            values.append(role)
        if status is not None:
            if status not in ("active", "disabled"):
                raise ValueError("status 必须是 active 或 disabled。")
            updates.append("status = ?")
            values.append(status)
        if password is not None and password != "":
            if len(password) < 8:
                raise ValueError("密码至少 8 个字符。")
            updates.append("password_hash = ?")
            values.append(self._ph.hash(password))
        if not updates:
            user = self.get_user(user_id)
            if user is None:
                raise ValueError("用户不存在。")
            return user
        updates.append("updated_at = ?")
        values.append(int(time.time()))
        values.append(int(user_id))
        with self._lock:
            cur = self.conn.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                tuple(values),
            )
            self.conn.commit()
            if cur.rowcount == 0:
                raise ValueError("用户不存在。")
            if status == "disabled":
                self.conn.execute(
                    "UPDATE sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at = 0",
                    (int(time.time()), int(user_id)),
                )
                self.conn.commit()
        user = self.get_user(user_id)
        if user is None:
            raise ValueError("用户不存在。")
        return user

    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        if not self.authenticate_password(user_id, old_password):
            raise ValueError("原密码不正确。")
        self.update_user(user_id, password=new_password)
        self.revoke_user_sessions(user_id)

    def authenticate(self, username: str, password: str) -> Optional[AuthUser]:
        name = self._clean_username(username)
        with self._lock:
            row = self.conn.execute(
                "SELECT id, username, password_hash, role, status FROM users WHERE username = ?",
                (name,),
            ).fetchone()
        if row is None or row["status"] != "active":
            return None
        try:
            ok = self._ph.verify(row["password_hash"], password or "")
        except (VerifyMismatchError, InvalidHashError):
            return None
        if not ok:
            return None
        if self._ph.check_needs_rehash(row["password_hash"]):
            self.update_user(int(row["id"]), password=password)
        now = int(time.time())
        with self._lock:
            self.conn.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now, int(row["id"])))
            self.conn.commit()
        return self._row_to_user(row)

    def authenticate_password(self, user_id: int, password: str) -> bool:
        with self._lock:
            row = self.conn.execute(
                "SELECT password_hash, status FROM users WHERE id = ?",
                (int(user_id),),
            ).fetchone()
        if row is None or row["status"] != "active":
            return False
        try:
            return bool(self._ph.verify(row["password_hash"], password or ""))
        except (VerifyMismatchError, InvalidHashError):
            return False

    def create_session(self, user_id: int, days: int = SESSION_DAYS_DEFAULT) -> SessionTokens:
        token = secrets.token_urlsafe(48)
        csrf_token = secrets.token_urlsafe(32)
        now = int(time.time())
        expires_at = now + max(1, int(days)) * 86400
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO sessions
                    (user_id, token_hash, csrf_hash, expires_at, created_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (int(user_id), hash_token(token), hash_token(csrf_token), expires_at, now, now),
            )
            self.conn.commit()
        return SessionTokens(token=token, csrf_token=csrf_token, expires_at=expires_at)

    def user_for_session(self, token: str) -> Optional[AuthUser]:
        digest = hash_token(token or "")
        now = int(time.time())
        with self._lock:
            row = self.conn.execute(
                """
                SELECT u.id, u.username, u.role, u.status, s.expires_at
                FROM sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.token_hash = ? AND s.revoked_at = 0
                """,
                (digest,),
            ).fetchone()
            if row is None or int(row["expires_at"]) <= now or row["status"] != "active":
                return None
            self.conn.execute(
                "UPDATE sessions SET last_seen_at = ? WHERE token_hash = ?",
                (now, digest),
            )
            self.conn.commit()
        return AuthUser(id=int(row["id"]), username=str(row["username"]), role=str(row["role"]), status=str(row["status"]))

    def validate_csrf(self, token: str, csrf_token: str) -> bool:
        if not token or not csrf_token:
            return False
        with self._lock:
            row = self.conn.execute(
                "SELECT csrf_hash, expires_at, revoked_at FROM sessions WHERE token_hash = ?",
                (hash_token(token),),
            ).fetchone()
        return (
            row is not None
            and int(row["revoked_at"]) == 0
            and int(row["expires_at"]) > int(time.time())
            and secrets.compare_digest(str(row["csrf_hash"]), hash_token(csrf_token))
        )

    def revoke_session(self, token: str) -> None:
        if not token:
            return
        with self._lock:
            self.conn.execute(
                "UPDATE sessions SET revoked_at = ? WHERE token_hash = ? AND revoked_at = 0",
                (int(time.time()), hash_token(token)),
            )
            self.conn.commit()

    def revoke_user_sessions(self, user_id: int) -> None:
        with self._lock:
            self.conn.execute(
                "UPDATE sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at = 0",
                (int(time.time()), int(user_id)),
            )
            self.conn.commit()

    def get_llm_config(self, user_id: int, store: Optional[SecretStore] = None) -> Dict[str, object]:
        with self._lock:
            row = self.conn.execute(
                "SELECT * FROM user_llm_configs WHERE user_id = ?",
                (int(user_id),),
            ).fetchone()
        if row is None:
            return {
                "base_url": DEFAULT_BASE_URL,
                "model": DEFAULT_MODEL,
                "max_tokens": DEFAULT_MAX_TOKENS,
                "advanced_model": "",
                "advanced_base_url": "",
                "has_api_key": False,
                "has_advanced_api_key": False,
                "api_key": "",
                "advanced_api_key": "",
            }
        api_key = ""
        advanced_api_key = ""
        if store is not None:
            api_key = store.decrypt(row["encrypted_api_key"])
            advanced_api_key = store.decrypt(row["encrypted_advanced_api_key"])
        return {
            "base_url": str(row["base_url"] or DEFAULT_BASE_URL),
            "model": str(row["model"] or DEFAULT_MODEL),
            "max_tokens": int(row["max_tokens"] or DEFAULT_MAX_TOKENS),
            "advanced_model": str(row["advanced_model"] or ""),
            "advanced_base_url": str(row["advanced_base_url"] or ""),
            "has_api_key": bool(row["encrypted_api_key"]),
            "has_advanced_api_key": bool(row["encrypted_advanced_api_key"]),
            "api_key": api_key,
            "advanced_api_key": advanced_api_key,
        }

    def build_llm_config(self, user_id: int, store: SecretStore) -> LLMConfig:
        cfg = self.get_llm_config(user_id, store)
        return LLMConfig(
            api_key=str(cfg["api_key"] or ""),
            base_url=normalize_openai_base_url(str(cfg["base_url"] or DEFAULT_BASE_URL)),
            model=str(cfg["model"] or DEFAULT_MODEL),
            max_tokens=int(cfg["max_tokens"] or DEFAULT_MAX_TOKENS),
            advanced_model=str(cfg["advanced_model"] or ""),
            advanced_base_url=normalize_openai_base_url(str(cfg["advanced_base_url"]))
            if str(cfg["advanced_base_url"] or "").strip()
            else "",
            advanced_api_key=str(cfg["advanced_api_key"] or ""),
        )

    def save_llm_config(
        self,
        user_id: int,
        store: SecretStore,
        *,
        base_url: str,
        model: str,
        api_key: Optional[str] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        advanced_model: str = "",
        advanced_base_url: str = "",
        advanced_api_key: Optional[str] = None,
    ) -> Dict[str, object]:
        existing = self.get_llm_config(user_id)
        clean_base = normalize_openai_base_url((base_url or str(existing["base_url"])).strip())
        clean_model = (model or str(existing["model"])).strip()
        clean_adv_base_in = (advanced_base_url or "").strip()
        clean_adv_base = normalize_openai_base_url(clean_adv_base_in) if clean_adv_base_in else ""
        encrypted_api_key = None
        encrypted_advanced_api_key = None
        if api_key is not None:
            encrypted_api_key = store.encrypt(api_key)
        if advanced_api_key is not None:
            encrypted_advanced_api_key = store.encrypt(advanced_api_key)
        with self._lock:
            row = self.conn.execute(
                "SELECT encrypted_api_key, encrypted_advanced_api_key FROM user_llm_configs WHERE user_id = ?",
                (int(user_id),),
            ).fetchone()
            if row is None:
                now = int(time.time())
                self.conn.execute(
                    """
                    INSERT INTO user_llm_configs
                        (user_id, base_url, model, max_tokens, advanced_model, advanced_base_url,
                         encrypted_api_key, encrypted_advanced_api_key, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(user_id),
                        clean_base,
                        clean_model,
                        int(max_tokens or DEFAULT_MAX_TOKENS),
                        (advanced_model or "").strip(),
                        clean_adv_base,
                        encrypted_api_key or "",
                        encrypted_advanced_api_key or "",
                        now,
                        now,
                    ),
                )
            else:
                updates = [
                    "base_url = ?",
                    "model = ?",
                    "max_tokens = ?",
                    "advanced_model = ?",
                    "advanced_base_url = ?",
                    "updated_at = ?",
                ]
                values: List[object] = [
                    clean_base,
                    clean_model,
                    int(max_tokens or DEFAULT_MAX_TOKENS),
                    (advanced_model or "").strip(),
                    clean_adv_base,
                    int(time.time()),
                ]
                if encrypted_api_key is not None:
                    updates.append("encrypted_api_key = ?")
                    values.append(encrypted_api_key)
                if encrypted_advanced_api_key is not None:
                    updates.append("encrypted_advanced_api_key = ?")
                    values.append(encrypted_advanced_api_key)
                values.append(int(user_id))
                self.conn.execute(
                    f"UPDATE user_llm_configs SET {', '.join(updates)} WHERE user_id = ?",
                    tuple(values),
                )
            self.conn.commit()
        return self.get_llm_config(user_id)

    @staticmethod
    def _clean_username(username: str) -> str:
        return (username or "").strip().lower()

    @staticmethod
    def _row_to_user(row: Optional[sqlite3.Row]) -> Optional[AuthUser]:
        if row is None:
            return None
        return AuthUser(
            id=int(row["id"]),
            username=str(row["username"]),
            role=str(row["role"]),
            status=str(row["status"]),
        )
