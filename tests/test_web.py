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

    def test_markdown_viewer_has_mermaid_lightbox_and_required_persistent_identity(self):
        source = WEB.read_text()
        for marker in ("marked", "mermaid", "class=\"mermaid\"", "markdown-content", "mermaid-lightbox", "identity-cover", "localStorage", "normalizeIdentity", "identity-edit"):
            self.assertIn(marker, source)

    def test_shared_feedback_is_default_off_and_owner_projected_only(self):
        source = WEB.read_text()
        self.assertIn("id=shared", source)
        self.assertIn("/api/shared-feedback", source)
        self.assertIn("shared_feedback_enabled", source)
        self.assertIn("--shared-feedback", source)
        self.assertIn("owner_results", source)


if __name__ == "__main__":
    unittest.main()
