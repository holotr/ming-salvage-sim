from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class UpstreamDockerPatchTests(unittest.TestCase):
    def test_upstream_dockerfile_builds_from_patched_branch(self):
        dockerfile = (ROOT / "Dockerfile.upstream").read_text(encoding="utf-8")
        patch_path = ROOT / "patches" / "upstream-streaming.patch"

        self.assertTrue(patch_path.exists())
        self.assertIn(
            "ARG UPSTREAM_REPO=https://github.com/holotr/ming-salvage-sim.git",
            dockerfile,
        )
        self.assertIn("ARG UPSTREAM_REF=codex/wanweiying3-stream-fk", dockerfile)
        self.assertNotIn("upstream-streaming.patch", dockerfile)
        self.assertNotIn("git apply", dockerfile)

    def test_upstream_streaming_patch_applies_to_upstream_main(self):
        patch_path = ROOT / "patches" / "upstream-streaming.patch"
        ref_check = subprocess.run(
            ["git", "rev-parse", "--verify", "upstream/main"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if ref_check.returncode != 0:
            self.skipTest("upstream/main ref is not available")

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
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
