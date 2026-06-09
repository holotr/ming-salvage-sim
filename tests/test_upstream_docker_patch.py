from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_upstream_dockerfile_applies_streaming_patch():
    dockerfile = (ROOT / "Dockerfile.upstream").read_text(encoding="utf-8")
    patch_path = ROOT / "patches" / "upstream-streaming.patch"

    assert patch_path.exists()
    assert "COPY patches/upstream-streaming.patch" in dockerfile
    assert "git apply /tmp/upstream-streaming.patch" in dockerfile


def test_upstream_streaming_patch_applies_to_upstream_main():
    patch_path = ROOT / "patches" / "upstream-streaming.patch"
    ref_check = subprocess.run(
        ["git", "rev-parse", "--verify", "upstream/main"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if ref_check.returncode != 0:
        pytest.skip("upstream/main ref is not available")

    source = subprocess.run(
        ["git", "show", "upstream/main:ming_sim/decree.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        target = tmp / "ming_sim" / "decree.py"
        target.parent.mkdir()
        target.write_text(source, encoding="utf-8")

        result = subprocess.run(
            ["git", "apply", "--check", str(patch_path)],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
    assert result.returncode == 0, result.stderr
