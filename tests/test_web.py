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

    def test_markdown_renderer_is_scoped_so_chrome_script_can_boot(self):
        source = WEB.read_text()
        self.assertIn("<script>(()=>", source)
        self.assertIn("})();</script>", source)
        chrome = (ROOT / "web" / "chrome.js").read_text()
        self.assertIn("function openDiagram", chrome)
        self.assertIn("window.openDiagram", chrome)

    def test_chrome_assets_keep_human_review_interaction_and_relay_boundary(self):
        html = (ROOT / "web" / "chrome.html").read_text()
        css = (ROOT / "web" / "chrome.css").read_text()
        js = (ROOT / "web" / "chrome.js").read_text()
        for marker in ("class=\"stage\"", "class=\"handle\"", "class=\"rail\"", "class=\"rail-scroll\"", "id=\"compose\"", "class=\"cards\"", "class=\"rail-foot\""):
            self.assertIn(marker, html)
        for marker in ("--canvas:#e8e4da", "--rail-w:352px", "rgba(224,173,39,.42)", "subspace-saved"):
            self.assertIn(marker, css)
        for marker in ("/api/submit", "Annotation", "feedback-only", "localStorage", "CSS.highlights", "Jump to"):
            self.assertIn(marker, js)

    def test_p1_human_review_parity_is_interactive_and_immutable_safe(self):
        html = (ROOT / "web" / "chrome.html").read_text()
        css = (ROOT / "web" / "chrome.css").read_text()
        js = (ROOT / "web" / "chrome.js").read_text()
        for marker in ('id="theme"', 'id="shared"', 'id="identity-chip"', 'id="composeKind"', 'id="team"', 'id="status"'):
            self.assertIn(marker, html)
        for marker in ('data-theme="dark"', '.remove', '.body-edit', '.send:disabled', '@media(max-width:800px)'):
            self.assertIn(marker, css)
        for marker in ('themeKey', 'toggleTheme', 'editComment', 'deleteComment', 'activateComment', 'keydown', 'Escape', 'Enter', 'showTeamFeedback', 'kind = "comment"'):
            self.assertIn(marker, js)
        self.assertNotIn('/api/page/', js)
        self.assertNotIn('artifact.innerHTML =', js)

    def test_annotation_draft_keeps_artifact_range_when_composer_focus_changes_selection(self):
        source = WEB.read_text()
        self.assertIn("artifact.contains(candidate.commonAncestorContainer)", source)
        self.assertIn("draftRange=range.cloneRange()", source)
        self.assertIn("savedRanges.push(draftRange)", source)

    def test_web_can_bind_to_explicit_tailnet_host_without_changing_default_loopback(self):
        source = WEB.read_text()
        self.assertIn('p.add_argument("--host",default="127.0.0.1")', source)
        self.assertIn("ThreadingHTTPServer((args.host,args.port),Handler)", source)

    def test_p3_uses_delegated_mermaid_lightbox_and_theme_aware_surfaces(self):
        source = WEB.read_text()
        css = (ROOT / "web" / "chrome.css").read_text()
        js = (ROOT / "web" / "chrome.js").read_text()
        self.assertIn("mermaid:open", source)
        self.assertIn("--artifact-bg", css)
        self.assertIn("--artifact-fg", css)
        self.assertIn("--diagram-fg", css)
        self.assertIn("width:min(100%,1024px)", css)
        self.assertIn("background:transparent", css)
        self.assertIn("closest('.mermaid svg')", js)
        self.assertIn("event.key === 'Escape'", js)

    def test_mermaid_has_theme_aware_edges_close_control_and_readable_failure(self):
        source = WEB.read_text()
        html = (ROOT / "web" / "chrome.html").read_text()
        css = (ROOT / "web" / "chrome.css").read_text()
        js = (ROOT / "web" / "chrome.js").read_text()
        for marker in ('lineColor', 'primaryBorderColor', 'edgeLabelBackground', 'Diagram could not render'):
            self.assertIn(marker, source)
        self.assertIn('id="diagram-close"', html)
        self.assertIn('.diagram-close', css)
        self.assertIn("$('diagram-close').onclick", js)

    def test_shared_feedback_is_default_off_and_owner_projected_only(self):
        source = WEB.read_text()
        self.assertIn("id=shared", source)
        self.assertIn("/api/shared-feedback", source)
        self.assertIn("args.shared_feedback", source)
        self.assertIn("--shared-feedback", source)
        self.assertIn("owner_results", source)


if __name__ == "__main__":
    unittest.main()
