import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
CLI = ROOT / "bin" / "subspace-review-relay"


def run(*args, check=True):
    return subprocess.run([sys.executable, str(CLI), *args], text=True, capture_output=True, check=check)


class RelayPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.artifact = self.root / "design-preview.html"
        self.artifact.write_bytes(b"<main>fixed design bytes</main>\n")
        self.briefing = self.root / "briefing.json"
        briefing = {
            "type": "Briefing", "version": "1", "id": "briefing:0123456789abcdef0123456789abcdef",
            "question": "Is this preview clear?",
            "artifacts": [{"id": "artifact:design", "uri": "design-preview.html", "mediaType": "text/html", "rev": "sha256:placeholder"}],
            "context": [],
        }
        self.briefing.write_text(json.dumps(briefing))
        import hashlib
        briefing["artifacts"][0]["rev"] = "sha256:" + hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        self.briefing.write_text(json.dumps(briefing))

    def tearDown(self):
        self.temp.cleanup()

    def test_package_emits_relay_manifest_with_relative_safe_uri_and_raw_hashes(self):
        result = run("package", "--briefing", str(self.briefing), "--output-dir", str(self.root / "package"))
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        manifest = json.loads((self.root / "package" / "manifest.json").read_text())
        self.assertEqual(manifest["type"], "subspace-relay-package")
        self.assertEqual(manifest["version"], "1")
        self.assertEqual(manifest["files"][0]["artifactId"], "artifact:design")
        self.assertEqual(manifest["files"][0]["uri"], "design-preview.html")
        self.assertEqual(manifest["files"][0]["size"], len(self.artifact.read_bytes()))
        self.assertTrue(manifest["briefingSha256"].startswith("sha256:"))
        self.assertEqual((self.root / "package" / "design-preview.html").read_bytes(), self.artifact.read_bytes())

    def test_package_refuses_absolute_artifact_uri(self):
        briefing = json.loads(self.briefing.read_text())
        briefing["artifacts"][0]["uri"] = str(self.artifact)
        self.briefing.write_text(json.dumps(briefing))
        result = run("package", "--briefing", str(self.briefing), "--output-dir", str(self.root / "package"), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("relative", result.stderr)

    def test_fetch_verifies_staging_style_package_from_local_http_server(self):
        package = self.root / "package"
        run("package", "--briefing", str(self.briefing), "--output-dir", str(package))
        # `fetch` accepts a base API endpoint for a local/staging Relay-compatible server.
        result = run("fetch", "--briefing", "briefing:0123456789abcdef0123456789abcdef", "--endpoint", "http://127.0.0.1:9", "--output-dir", str(self.root / "fetched"), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fetch failed", result.stderr)

    def test_publish_dry_run_creates_private_owner_receipt_without_network(self):
        package = self.root / "package"
        run("package", "--briefing", str(self.briefing), "--output-dir", str(package))
        state = self.root / "state"
        result = run("publish", "--package", str(package), "--state-dir", str(state), "--endpoint", "https://relay.example", "--dry-run")
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        receipt = state / "owners" / f"{payload['briefing']}.json"
        self.assertTrue(receipt.is_file())
        saved = json.loads(receipt.read_text())
        self.assertRegex(saved["deviceId"], r"^dev_[a-z2-7]{26}$")
        self.assertRegex(saved["deviceSecret"], r"^sec_[a-z2-7]{52}$")
        self.assertFalse("deviceSecret" in result.stdout)

    def test_annotations_accept_native_human_review_feedback_with_explicit_actor(self):
        feedback = self.root / "human-review.json"
        feedback.write_text(json.dumps({"pages": [{"comments": [{"quote": "fixed design", "anchor": {"prefix": "<main>", "quote": "fixed design", "suffix": " bytes"}, "feedback": "Clarify this label."}]}]}))
        run("annotations", "--briefing", str(self.briefing), "--feedback", str(feedback), "--reviewer", "person:reviewer", "--output", str(self.root / "review.jsonl"))
        entry = json.loads((self.root / "review.jsonl").read_text().splitlines()[0])
        self.assertEqual(entry["by"], "person:reviewer")
        self.assertEqual(entry["selectors"][0]["exact"], "fixed design")

    def test_annotation_converts_browser_comment_to_portable_jsonl(self):
        feedback = self.root / "feedback.json"
        feedback.write_text(json.dumps({
            "reviewer": "person:reviewer",
            "comments": [{"quote": "fixed design", "prefix": "<main>", "suffix": " bytes", "feedback": "Clarify this label."}],
            "overall_note": "Works for me.",
        }))
        result = run("annotations", "--briefing", str(self.briefing), "--feedback", str(feedback), "--output", str(self.root / "review.jsonl"))
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        entries = [json.loads(line) for line in (self.root / "review.jsonl").read_text().splitlines()]
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["type"], "Annotation")
        self.assertEqual(entries[0]["target"], "artifact:design")
        self.assertEqual(entries[0]["selectors"][0]["type"], "TextQuoteSelector")
        self.assertEqual(entries[1]["body"], "Works for me.")


if __name__ == "__main__":
    unittest.main()
