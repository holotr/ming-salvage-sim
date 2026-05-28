#!/usr/bin/env python3
"""Container entrypoint: prepare writable data dirs, then drop privileges."""

from __future__ import annotations

import os
import pwd
import sys
from pathlib import Path


RUN_USER = os.environ.get("MING_SIM_RUN_USER", "app")
DATA_DIR = os.environ.get("MING_SIM_DATA_DIR", "/app/data")


def _prepare_paths() -> set[Path]:
    paths = {Path(DATA_DIR)}
    auth_db = os.environ.get("MING_SIM_AUTH_DB", "").strip()
    if auth_db:
        parent = Path(auth_db).parent
        if str(parent) not in ("", "."):
            paths.add(parent)
    return paths


def _chown_tree(path: Path, uid: int, gid: int) -> None:
    path.mkdir(parents=True, exist_ok=True)
    os.chown(path, uid, gid)
    for root, dirs, files in os.walk(path):
        for name in [*dirs, *files]:
            target = os.path.join(root, name)
            try:
                os.chown(target, uid, gid)
            except FileNotFoundError:
                continue


def _drop_to_user(username: str) -> None:
    account = pwd.getpwnam(username)
    os.setgroups([])
    os.setgid(account.pw_gid)
    os.setuid(account.pw_uid)
    os.environ["HOME"] = account.pw_dir


def main() -> int:
    if len(sys.argv) < 2:
        print("docker-entrypoint.py: no command supplied", file=sys.stderr)
        return 64

    if os.getuid() == 0:
        account = pwd.getpwnam(RUN_USER)
        for path in _prepare_paths():
            _chown_tree(path, account.pw_uid, account.pw_gid)
        _drop_to_user(RUN_USER)

    os.execvp(sys.argv[1], sys.argv[1:])
    return 127


if __name__ == "__main__":
    raise SystemExit(main())
