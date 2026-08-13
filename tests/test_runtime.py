import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
RUNTIME = ROOT / "bin" / "subspace-review-runtime"


def run(*args, check=True, env=None):
    return subprocess.run(
        [sys.executable, str(RUNTIME), *args],
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=True,
        env=env,
    )


class RuntimeTests(unittest.TestCase):
    def test_doctor_reports_missing_commands_as_machine_readable_failure(self):
        env = {**os.environ, "PATH": "/nonexistent"}
        result = run("doctor", check=False, env=env)
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(payload["ok"])
        self.assertIn("node", payload["missing"])
        self.assertIn("cloudflared", payload["missing"])
        self.assertIn("curl", payload["missing"])

    def test_open_requires_existing_artifact_before_starting_any_process(self):
        result = run("open", "--artifact", "/definitely/missing.html", check=False)
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(payload["ok"])
        self.assertIn("artifact not found", payload["error"])

    def test_status_of_unknown_state_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run("status", "--state-dir", directory, check=False)
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(payload["ok"])
        self.assertIn("no active review", payload["error"])


if __name__ == "__main__":
    unittest.main()
