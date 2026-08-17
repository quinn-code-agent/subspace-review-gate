import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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

    def test_create_room_uses_private_owner_receipt_and_frozen_owner_route(self):
        briefing_id = "briefing:0123456789abcdef0123456789abcdef"
        state = self.root / "state"
        receipt = state / "owners" / f"{briefing_id}.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({
            "briefing": briefing_id,
            "endpoint": "http://unused.example",
            "deviceId": "dev_aaaaaaaaaaaaaaaaaaaaaaaaaa",
            "deviceSecret": "sec_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        }))

        seen = {}
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                seen["path"] = self.path
                seen["device"] = self.headers.get("X-Subspace-Device")
                seen["authorization"] = self.headers.get("Authorization")
                seen["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                raw = json.dumps({"roomId": "room_aaaaaaaaaaaaaaaaaaaaaaaaaa", "briefingId": briefing_id, "origin": "http://127.0.0.1"}).encode()
                self.send_response(201); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
            def log_message(self, *_): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            endpoint = f"http://127.0.0.1:{server.server_port}"
            result = run("create-room", "--briefing", briefing_id, "--state-dir", str(state), "--endpoint", endpoint)
        finally:
            server.shutdown(); thread.join(); server.server_close()
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["room_id"], "room_aaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.assertEqual(seen["path"], "/api/room")
        self.assertEqual(seen["body"], {"briefingId": briefing_id})
        self.assertEqual(seen["device"], "dev_aaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.assertEqual(seen["authorization"], "Bearer sec_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        self.assertNotIn("sec_", result.stdout)

    def test_disable_room_and_revoke_session_use_the_two_frozen_owner_routes(self):
        briefing_id = "briefing:0123456789abcdef0123456789abcdef"
        state = self.root / "state"
        receipt = state / "owners" / f"{briefing_id}.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({"briefing": briefing_id, "endpoint": "http://unused.example", "deviceId": "dev_aaaaaaaaaaaaaaaaaaaaaaaaaa", "deviceSecret": "sec_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}))
        seen = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                seen.append((self.path, self.headers.get("X-Subspace-Device"), self.headers.get("Authorization")))
                payload = {"disabledAt": "2026-08-18T00:00:00Z"} if self.path.endswith("/disable") else {"revokedAt": "2026-08-18T00:01:00Z"}
                raw = json.dumps(payload).encode()
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
            def log_message(self, *_): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            endpoint = f"http://127.0.0.1:{server.server_port}"
            disabled = run("disable-room", "--briefing", briefing_id, "--room-id", "room_aaaaaaaaaaaaaaaaaaaaaaaaaa", "--state-dir", str(state), "--endpoint", endpoint)
            revoked = run("revoke-room-session", "--briefing", briefing_id, "--room-id", "room_aaaaaaaaaaaaaaaaaaaaaaaaaa", "--session-id", "ses_bbbbbbbbbbbbbbbbbbbbbbbbbb", "--state-dir", str(state), "--endpoint", endpoint)
        finally:
            server.shutdown(); thread.join(); server.server_close()
        self.assertEqual(json.loads(disabled.stdout)["disabled_at"], "2026-08-18T00:00:00Z")
        self.assertEqual(json.loads(revoked.stdout)["revoked_at"], "2026-08-18T00:01:00Z")
        self.assertEqual(seen, [
            ("/api/room/room_aaaaaaaaaaaaaaaaaaaaaaaaaa/disable", "dev_aaaaaaaaaaaaaaaaaaaaaaaaaa", "Bearer sec_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"),
            ("/api/room/room_aaaaaaaaaaaaaaaaaaaaaaaaaa/session/ses_bbbbbbbbbbbbbbbbbbbbbbbbbb/revoke", "dev_aaaaaaaaaaaaaaaaaaaaaaaaaa", "Bearer sec_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"),
        ])

    def test_results_preserve_raw_summaries_and_render_participant_beside_claimed_name(self):
        briefing_id = "briefing:0123456789abcdef0123456789abcdef"
        state = self.root / "state"
        receipt = state / "owners" / f"{briefing_id}.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({"briefing": briefing_id, "endpoint": "http://unused.example", "deviceId": "dev_aaaaaaaaaaaaaaaaaaaaaaaaaa", "deviceSecret": "sec_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}))
        raw_results = [{"resultId": "res_aaaaaaaaaaaaaaaaaaaaaaaaaa", "actor": "person:kent", "participant": "par_bbbbbbbbbbbbbbbbbbbbbbbbbb"}]
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                raw = json.dumps({"results": raw_results, "listStale": False}).encode()
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
            def log_message(self, *_): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            result = run("results", "--briefing", briefing_id, "--state-dir", str(state), "--endpoint", f"http://127.0.0.1:{server.server_port}")
        finally:
            server.shutdown(); thread.join(); server.server_close()
        payload = json.loads(result.stdout)
        self.assertEqual(payload["results"], raw_results)
        self.assertEqual(payload["operator_summaries"], [{
            "result_id": "res_aaaaaaaaaaaaaaaaaaaaaaaaaa",
            "claimed_name": "person:kent",
            "participant": "par_bbbbbbbbbbbbbbbbbbbbbbbbbb",
            "attribution": "person:kent (self-declared) · par_bbbbbbbbbbbbbbbbbbbbbbbbbb",
        }])

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
