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


class Phase2ResultTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.briefing = self.root / "briefing.json"
        self.briefing.write_text(json.dumps({
            "type": "Briefing", "version": "1", "id": "briefing:0123456789abcdef0123456789abcdef",
            "question": "Review?",
            "artifacts": [{"id": "artifact:primary", "uri": "artifact.html", "mediaType": "text/html", "rev": "sha256:abc"}],
            "context": [],
        }))
        self.review = self.root / "review.jsonl"
        self.review.write_text(json.dumps({"type": "Annotation", "id": "annotation:one", "briefing": "briefing:0123456789abcdef0123456789abcdef", "by": "person:reviewer", "at": "2026-08-13T00:00:00Z", "target": "artifact:primary", "kind": "comment", "body": "Looks good."}) + "\n")

    def tearDown(self):
        self.temp.cleanup()

    def test_annotations_preserve_immutable_suggestion_kind(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            artifact = temp / "artifact.html"; artifact.write_text("<p>Hello</p>")
            digest = __import__("hashlib").sha256(artifact.read_bytes()).hexdigest()
            briefing = temp / "briefing.json"; briefing.write_text(__import__("json").dumps({"type":"Briefing","version":"1","id":"briefing:" + "a" * 32,"artifacts":[{"id":"artifact:one","uri":"artifact.html","mediaType":"text/html","rev":"sha256:" + digest}]}))
            feedback = temp / "feedback.json"; feedback.write_text(__import__("json").dumps({"comments":[{"quote":"Hello","feedback":"Use a friendlier greeting","kind":"suggestion"}]}))
            output = temp / "review.jsonl"
            result = subprocess.run([sys.executable, str(ROOT / "bin" / "subspace-review-relay"), "annotations", "--briefing", str(briefing), "--feedback", str(feedback), "--reviewer", "person:kc", "--output", str(output)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(__import__("json").loads(output.read_text())["kind"], "suggestion")

    def test_build_feedback_result_uses_subspace_result_shape_and_forbids_resolution(self):
        output = self.root / "result.json"
        result = run("build-feedback-result", "--briefing", str(self.briefing), "--review", str(self.review), "--actor", "person:reviewer", "--output", str(output))
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        value = json.loads(output.read_text())
        self.assertEqual(value["type"], "review-v1-result")
        self.assertEqual(value["mode"], "feedback")
        self.assertEqual(value["briefing"], "briefing:0123456789abcdef0123456789abcdef")
        self.assertEqual(value["actor"], "person:reviewer")
        self.assertEqual(value["annotations"][0]["id"], "annotation:one")
        self.assertNotIn("resolution", value)

    def test_submit_dry_run_keeps_reviewer_secret_private(self):
        result_path = self.root / "result.json"
        run("build-feedback-result", "--briefing", str(self.briefing), "--review", str(self.review), "--actor", "person:reviewer", "--output", str(result_path))
        state = self.root / "state"
        response = run("submit", "--briefing", "briefing:0123456789abcdef0123456789abcdef", "--review", str(self.review), "--result", str(result_path), "--state-dir", str(state), "--endpoint", "https://relay.example", "--dry-run")
        payload = json.loads(response.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue((state / "reviewers" / "briefing:0123456789abcdef0123456789abcdef.json").is_file())
        self.assertNotIn("sec_", response.stdout)

    def test_build_feedback_result_rejects_resolution_entry(self):
        self.review.write_text(json.dumps({"type": "Resolution", "id": "resolution:no", "briefing": "briefing:0123456789abcdef0123456789abcdef", "by": "person:reviewer", "at": "2026-08-13T00:00:00Z", "decision": "approve"}) + "\n")
        result = run("build-feedback-result", "--briefing", str(self.briefing), "--review", str(self.review), "--actor", "person:reviewer", "--output", str(self.root / "result.json"), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot contain a Resolution", result.stderr)


if __name__ == "__main__":
    unittest.main()
