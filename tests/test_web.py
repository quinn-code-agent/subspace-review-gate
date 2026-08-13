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

    def test_web_reviewer_has_cross_device_annotations_and_integrated_identity(self):
        source = WEB.read_text()
        for marker in (
            "marked", "mermaid", "markdown-content", "diagram-lightbox",
            "identity-cover", "localStorage", "norm(", "identity-edit", "identity-chip",
            "annotation-toolbar", "mobile-comment-action", "mobile-sheet", "CSS.highlights",
            "annotation-color", "railKey", "subspace-draft",
        ):
            self.assertIn(marker, source)

    def test_annotation_draft_keeps_artifact_range_when_composer_focus_changes_selection(self):
        source = WEB.read_text()
        self.assertIn("artifact.contains(candidate.commonAncestorContainer)", source)
        self.assertIn("draftRange=range.cloneRange()", source)
        self.assertIn("savedRanges.push(draftRange)", source)

    def test_shared_feedback_is_default_off_and_owner_projected_only(self):
        source = WEB.read_text()
        self.assertIn("id=shared", source)
        self.assertIn("/api/shared-feedback", source)
        self.assertIn("args.shared_feedback", source)
        self.assertIn("--shared-feedback", source)
        self.assertIn("owner_results", source)


if __name__ == "__main__":
    unittest.main()
