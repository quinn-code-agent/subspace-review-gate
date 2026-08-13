import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
WEB = ROOT / "bin" / "subspace-relay-web"


class RelayWebTests(unittest.TestCase):
    def test_help_exposes_relay_backed_web_viewer_without_human_review_protocol(self):
        result = subprocess.run([sys.executable, str(WEB), "--help"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Relay-backed", result.stdout)
        self.assertIn("feedback-only", result.stdout)


if __name__ == "__main__":
    unittest.main()
