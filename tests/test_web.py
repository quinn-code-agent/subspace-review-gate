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

    def test_reviewer_identity_is_collected_per_browser_session_not_cli_wide(self):
        source = WEB.read_text()
        self.assertIn("id=reviewer", source)
        self.assertIn('reviewer=data.get("reviewer", "")', source)
        self.assertIn("reviewer_state", source)
        self.assertNotIn('parser.add_argument("--reviewer", required=True)', source)


if __name__ == "__main__":
    unittest.main()
