import hashlib
import importlib.machinery
import importlib.util
import json
import os
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


def load_plugin():
    spec = importlib.util.spec_from_file_location("subspace_review_gate_plugin", ROOT / "__init__.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RelayConsentOperationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.artifact = self.root / "review.md"
        self.artifact.write_text("# Fixed review\n")
        self.revision = "sha256:" + hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        self.state = self.root / "state"
        self.briefing = self.root / "briefing.json"
        self.package = self.root / "package"

    def tearDown(self):
        self.temp.cleanup()

    def share_args(self, endpoint):
        return (
            "share-consented", "--artifact", str(self.artifact), "--question", "Ready?",
            "--briefing", str(self.briefing), "--package", str(self.package),
            "--consent", "Yes", "--audience", "the bound Slack thread",
            "--consented-revision", self.revision, "--media-type", "text/markdown",
            "--sensitivity", "non-sensitive", "--endpoint", endpoint, "--state-dir", str(self.state),
        )

    def test_expired_authoritative_room_expiry_refuses_and_is_not_cached(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(inner):
                inner.reply({"oneArtifact": True, "acceptedMediaTypes": ["text/markdown"],
                             "maxArtifactBytes": 4096, "roomUrlResponse": True, "expiresAtResponse": True})
            def do_POST(inner):
                if inner.path == "/api/briefing":
                    inner.reply({"briefingId": json.loads(self.briefing.read_text())["id"],
                                 "shareUrl": "https://relay.invalid/r/private"}, 201)
                else:
                    inner.reply({"roomId": "room_aaaaaaaaaaaaaaaaaaaaaaaaaa",
                                 "briefingId": json.loads(self.briefing.read_text())["id"],
                                 "origin": "https://relay.example", "roomUrl": "https://relay.example/room/safe",
                                 "expiresAt": "2020-01-01T00:00:00Z"}, 201)
            def reply(inner, payload, status=200):
                raw = json.dumps(payload).encode(); inner.send_response(status)
                inner.send_header("Content-Length", str(len(raw))); inner.end_headers(); inner.wfile.write(raw)
            def log_message(self, format, *args): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            result = run(*self.share_args(f"http://127.0.0.1:{server.server_port}"), check=False)
        finally:
            server.shutdown(); thread.join(); server.server_close()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no shareable URL", result.stderr)
        self.assertFalse(any((self.state / "operations").rglob("*.json")))

    def test_clear_yes_runs_preflight_and_returns_only_safe_room_url_and_expiry(self):
        seen = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(inner):
                seen.append(("GET", inner.path))
                body = {
                    "oneArtifact": True,
                    "acceptedMediaTypes": ["text/markdown"],
                    "maxArtifactBytes": 4096,
                    "roomUrlResponse": True,
                    "expiresAtResponse": True,
                }
                inner.reply(body)
            def do_POST(inner):
                seen.append(("POST", inner.path))
                if inner.path == "/api/briefing":
                    inner.reply({"briefingId": json.loads(self.briefing.read_text())["id"], "shareUrl": "https://relay.invalid/r/private"}, 201)
                elif inner.path == "/api/room":
                    inner.reply({
                        "roomId": "room_aaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "briefingId": json.loads(self.briefing.read_text())["id"],
                        "origin": f"http://127.0.0.1:{server.server_port}",
                        "roomUrl": "https://relay.example/room/safe-capability",
                        "expiresAt": "2026-09-20T08:00:00.123Z",
                    }, 201)
                else:
                    inner.send_error(404)
            def reply(inner, payload, status=200):
                raw = json.dumps(payload).encode()
                inner.send_response(status)
                inner.send_header("Content-Type", "application/json")
                inner.send_header("Content-Length", str(len(raw)))
                inner.end_headers()
                inner.wfile.write(raw)
            def log_message(self, format, *args): pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            result = run(
                "share-consented", "--artifact", str(self.artifact), "--question", "Ready?",
                "--briefing", str(self.briefing), "--package", str(self.package),
                "--consent", "Yes, share it", "--audience", "the bound Slack thread",
                "--consented-revision", self.revision, "--media-type", "text/markdown", "--sensitivity", "non-sensitive",
                "--endpoint", f"http://127.0.0.1:{server.server_port}", "--state-dir", str(self.state),
            )
            replay = run(
                "share-consented", "--artifact", str(self.artifact), "--question", "Ready?",
                "--briefing", str(self.briefing), "--package", str(self.package),
                "--consent", "Yes", "--audience", "the bound Slack thread",
                "--consented-revision", self.revision, "--media-type", "text/markdown", "--sensitivity", "non-sensitive",
                "--endpoint", f"http://127.0.0.1:{server.server_port}", "--state-dir", str(self.state),
            )
        finally:
            server.shutdown(); thread.join(); server.server_close()
        payload = json.loads(result.stdout)
        self.assertEqual(payload, {
            "ok": True,
            "room_url": "https://relay.example/room/safe-capability",
            "expires_at": "2026-09-20T08:00:00Z",
        })
        self.assertEqual(json.loads(replay.stdout), payload)
        self.assertEqual([item[1] for item in seen], ["/api/capabilities/review-room", "/api/briefing", "/api/room"])
        self.assertNotIn("roomref_", result.stdout)
        self.assertNotIn("deviceSecret", result.stdout)
        self.assertNotIn(str(self.root), result.stdout)

    def test_ambiguous_consent_refuses_before_network_or_file_creation(self):
        result = run(
            "share-consented", "--artifact", str(self.artifact), "--question", "Ready?",
            "--briefing", str(self.briefing), "--package", str(self.package),
            "--consent", "sounds good", "--audience", "reviewers",
            "--consented-revision", self.revision, "--media-type", "text/markdown", "--sensitivity", "non-sensitive",
            "--endpoint", "http://127.0.0.1:9", "--state-dir", str(self.state), check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("clear Yes", result.stderr)
        self.assertFalse(self.briefing.exists())
        self.assertFalse(self.package.exists())

    def test_unknown_preflight_fails_closed_without_upload_or_shareable_url(self):
        class Handler(BaseHTTPRequestHandler):
            posts = 0
            def do_GET(inner):
                raw = json.dumps({"oneArtifact": True}).encode()
                inner.send_response(200); inner.send_header("Content-Length", str(len(raw))); inner.end_headers(); inner.wfile.write(raw)
            def do_POST(inner):
                Handler.posts += 1; inner.send_error(500)
            def log_message(self, format, *args): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            result = run(
                "share-consented", "--artifact", str(self.artifact), "--question", "Ready?",
                "--briefing", str(self.briefing), "--package", str(self.package),
                "--consent", "Yes", "--audience", "reviewers",
                "--consented-revision", self.revision, "--media-type", "text/markdown", "--sensitivity", "non-sensitive",
                "--endpoint", f"http://127.0.0.1:{server.server_port}", "--state-dir", str(self.state), check=False,
            )
        finally:
            server.shutdown(); thread.join(); server.server_close()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("capability preflight", result.stderr)
        self.assertNotIn("http", result.stdout)
        self.assertEqual(Handler.posts, 0)


class RelayFeedbackWatcherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.state = self.root / "state"
        self.briefing_id = "briefing:0123456789abcdef0123456789abcdef"
        self.room_ref = "roomref_aaaaaaaaaaaaaaaaaaaaaaaaaa"
        self.room_id = "room_aaaaaaaaaaaaaaaaaaaaaaaaaa"
        self.result_id = "res_bbbbbbbbbbbbbbbbbbbbbbbbbb"
        self.artifact = {"id": "artifact:review", "uri": "review.md", "mediaType": "text/markdown", "rev": "sha256:" + "a" * 64}
        package = self.root / "package"; package.mkdir()
        (package / "briefing.json").write_text(json.dumps({"type": "Briefing", "version": "1", "id": self.briefing_id, "artifacts": [self.artifact]}))
        owner = self.state / "owners" / f"{self.briefing_id}.json"; owner.parent.mkdir(parents=True)
        owner.write_text(json.dumps({"briefing": self.briefing_id, "endpoint": "http://unused", "deviceId": "dev_" + "a" * 26, "deviceSecret": "sec_" + "b" * 52, "package": str(package)}))
        os.chmod(owner, 0o600)
        room = self.state / "rooms" / self.briefing_id / f"{self.room_ref}.json"; room.parent.mkdir(parents=True)
        room.write_text(json.dumps({"briefing": self.briefing_id, "endpoint": "http://unused", "roomId": self.room_id, "expiresAt": "2099-01-01T00:00:00Z"}))
        os.chmod(room, 0o600)

    def tearDown(self):
        self.temp.cleanup()

    def test_owner_secret_state_with_group_or_world_permissions_refuses(self):
        owner = self.state / "owners" / f"{self.briefing_id}.json"
        os.chmod(owner, 0o644)
        result = run("watch-feedback-once", "--briefing", self.briefing_id, "--room-ref", self.room_ref,
                     "--origin-channel", "C123", "--origin-thread", "1.2", "--outbox", str(self.root / "outbox"),
                     "--state-dir", str(self.state), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("private permissions", result.stderr)

    def test_room_scoped_watcher_verifies_exact_bytes_emits_safe_event_and_dedupes(self):
        review = b'{"type":"Annotation","body":"untrusted raw feedback"}\n'
        result_bytes = (json.dumps({"id": self.result_id, "type": "review-v1-result", "mode": "feedback", "briefing": self.briefing_id, "artifact": self.artifact, "annotations": [{"type": "Annotation", "body": "untrusted raw feedback"}], "actor": "person:reviewer"}, separators=(",", ":")) + "\n").encode()
        class Handler(BaseHTTPRequestHandler):
            def do_GET(inner):
                if inner.path.endswith("/results"):
                    payload = {"results": [{"resultId": self.result_id, "roomId": self.room_id, "reviewSha256": hashlib.sha256(review).hexdigest(), "resultSha256": hashlib.sha256(result_bytes).hexdigest()}]}
                    raw = json.dumps(payload).encode()
                elif inner.path.endswith("/review.jsonl"): raw = review
                elif inner.path.endswith("/result.json"): raw = result_bytes
                else: inner.send_error(404); return
                inner.send_response(200); inner.send_header("Content-Length", str(len(raw))); inner.end_headers(); inner.wfile.write(raw)
            def log_message(self, format, *args): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        room_path = self.state / "rooms" / self.briefing_id / f"{self.room_ref}.json"
        room_data = json.loads(room_path.read_text()); room_data["endpoint"] = f"http://127.0.0.1:{server.server_port}"; room_path.write_text(json.dumps(room_data))
        outbox = self.root / "outbox.jsonl"
        command = (
            "watch-feedback-once", "--briefing", self.briefing_id, "--room-ref", self.room_ref,
            "--origin-channel", "C123", "--origin-thread", "1720000000.000001",
            "--outbox", str(outbox), "--state-dir", str(self.state),
        )
        try:
            first = run(*command)
            cursor = self.state / "watchers" / self.briefing_id / f"{self.room_ref}.json"
            cursor.unlink()  # simulate a crash after durable outbox append but before cursor persistence
            second = run(*command)
        finally:
            server.shutdown(); thread.join(); server.server_close()
        self.assertEqual(json.loads(first.stdout)["delivered"], 1)
        self.assertEqual(json.loads(second.stdout)["delivered"], 0)
        events = [json.loads(line) for line in outbox.read_text().splitlines()]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["origin"], {"channel": "C123", "thread": "1720000000.000001"})
        self.assertEqual(events[0]["message"], "Relay feedback received for the fixed review artifact. Feedback is advisory; no workflow state changed.")
        self.assertNotIn("untrusted raw feedback", outbox.read_text())
        cursor = self.state / "watchers" / self.briefing_id / f"{self.room_ref}.json"
        self.assertIn(self.result_id, json.loads(cursor.read_text())["processedResultIds"])

    def test_watcher_refuses_pulled_result_whose_embedded_id_differs_from_listed_id(self):
        review = b'{}\n'
        result_bytes = (json.dumps({"id": "res_cccccccccccccccccccccccccccc", "type": "review-v1-result",
                                    "mode": "feedback", "briefing": self.briefing_id, "artifact": self.artifact,
                                    "annotations": [{}]}, separators=(",", ":")) + "\n").encode()
        class Handler(BaseHTTPRequestHandler):
            def do_GET(inner):
                if inner.path.endswith("/results"):
                    raw = json.dumps({"results": [{"resultId": self.result_id, "roomId": self.room_id,
                        "reviewSha256": hashlib.sha256(review).hexdigest(),
                        "resultSha256": hashlib.sha256(result_bytes).hexdigest()}]}).encode()
                elif inner.path.endswith("/review.jsonl"): raw = review
                else: raw = result_bytes
                inner.send_response(200); inner.send_header("Content-Length", str(len(raw))); inner.end_headers(); inner.wfile.write(raw)
            def log_message(self, format, *args): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        room_path = self.state / "rooms" / self.briefing_id / f"{self.room_ref}.json"
        room = json.loads(room_path.read_text()); room["endpoint"] = f"http://127.0.0.1:{server.server_port}"
        room_path.write_text(json.dumps(room)); os.chmod(room_path, 0o600)
        try:
            result = run("watch-feedback-once", "--briefing", self.briefing_id, "--room-ref", self.room_ref,
                         "--origin-channel", "C123", "--origin-thread", "1.2", "--outbox", str(self.root / "outbox"),
                         "--state-dir", str(self.state), check=False)
        finally:
            server.shutdown(); thread.join(); server.server_close()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Result identity", result.stderr)

    def test_credentialed_watcher_request_refuses_redirect(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(inner):
                if inner.path.endswith("/results"):
                    inner.send_response(302); inner.send_header("Location", "/redirected"); inner.end_headers()
                else:
                    raw = b'{"results":[]}'
                    inner.send_response(200); inner.send_header("Content-Length", str(len(raw))); inner.end_headers(); inner.wfile.write(raw)
            def log_message(self, format, *args): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        room_path = self.state / "rooms" / self.briefing_id / f"{self.room_ref}.json"
        room = json.loads(room_path.read_text()); room["endpoint"] = f"http://127.0.0.1:{server.server_port}"
        room_path.write_text(json.dumps(room)); os.chmod(room_path, 0o600)
        try:
            result = run("watch-feedback-once", "--briefing", self.briefing_id, "--room-ref", self.room_ref,
                         "--origin-channel", "C123", "--origin-thread", "1.2", "--outbox", str(self.root / "outbox"),
                         "--state-dir", str(self.state), check=False)
        finally:
            server.shutdown(); thread.join(); server.server_close()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("redirect", result.stderr.lower())

    def test_watcher_cursor_freezes_origin_and_outbox_binding(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(inner):
                raw = b'{"results":[]}'
                inner.send_response(200); inner.send_header("Content-Length", str(len(raw))); inner.end_headers(); inner.wfile.write(raw)
            def log_message(self, format, *args): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        room_path = self.state / "rooms" / self.briefing_id / f"{self.room_ref}.json"
        room = json.loads(room_path.read_text()); room["endpoint"] = f"http://127.0.0.1:{server.server_port}"
        room_path.write_text(json.dumps(room)); os.chmod(room_path, 0o600)
        try:
            first = run("watch-feedback-once", "--briefing", self.briefing_id, "--room-ref", self.room_ref,
                        "--origin-channel", "C_ORIGINAL", "--origin-thread", "1.1", "--outbox", str(self.root / "outbox-a"),
                        "--state-dir", str(self.state))
            rebound = run("watch-feedback-once", "--briefing", self.briefing_id, "--room-ref", self.room_ref,
                          "--origin-channel", "C_OTHER", "--origin-thread", "9.9", "--outbox", str(self.root / "outbox-b"),
                          "--state-dir", str(self.state), check=False)
        finally:
            server.shutdown(); thread.join(); server.server_close()
        self.assertEqual(json.loads(first.stdout)["delivered"], 0)
        self.assertNotEqual(rebound.returncode, 0)
        self.assertIn("binding", rebound.stderr)

    def test_background_watcher_start_is_ready_idempotent_and_stop_is_verified(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(inner):
                raw = b'{"results":[]}'
                inner.send_response(200); inner.send_header("Content-Length", str(len(raw))); inner.end_headers(); inner.wfile.write(raw)
            def log_message(self, format, *args): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        room_path = self.state / "rooms" / self.briefing_id / f"{self.room_ref}.json"
        room = json.loads(room_path.read_text()); room["endpoint"] = f"http://127.0.0.1:{server.server_port}"
        room_path.write_text(json.dumps(room)); os.chmod(room_path, 0o600)
        plugin = load_plugin()
        args = {"briefing": self.briefing_id, "room_ref": self.room_ref, "origin_channel": "C123",
                "origin_thread": "1.2", "outbox": str(self.root / "outbox"), "state_dir": str(self.state),
                "interval": 0.05}
        pids = []
        try:
            first = json.loads(plugin.relay_watch_feedback(args))
            pids.append(first["pid"])
            second = json.loads(plugin.relay_watch_feedback(args))
            pids.append(second["pid"])
            self.assertTrue(first["ready"])
            self.assertEqual(second["pid"], first["pid"])
            self.assertTrue(second["reused"])
            rebound = json.loads(plugin.relay_watch_feedback({**args, "origin_thread": "9.9"}))
            self.assertFalse(rebound["ok"])
            stopped = json.loads(plugin.relay_stop_feedback_watch({"briefing": self.briefing_id,
                "room_ref": self.room_ref, "state_dir": str(self.state)}))
            self.assertTrue(stopped["shutdown_verified"])
            with self.assertRaises(ProcessLookupError): os.kill(first["pid"], 0)
        finally:
            server.shutdown(); thread.join(); server.server_close()
            for pid in set(pids):
                try: os.kill(pid, 15)
                except ProcessLookupError: pass

    def test_watcher_ignores_result_without_matching_room_and_does_not_advance_cursor(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(inner):
                raw = json.dumps({"results": [{"resultId": self.result_id, "roomId": "room_cccccccccccccccccccccccccc", "reviewSha256": "0" * 64, "resultSha256": "1" * 64}]}).encode()
                inner.send_response(200); inner.send_header("Content-Length", str(len(raw))); inner.end_headers(); inner.wfile.write(raw)
            def log_message(self, format, *args): pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        room_path = self.state / "rooms" / self.briefing_id / f"{self.room_ref}.json"
        room_data = json.loads(room_path.read_text()); room_data["endpoint"] = f"http://127.0.0.1:{server.server_port}"; room_path.write_text(json.dumps(room_data))
        outbox = self.root / "outbox.jsonl"
        try:
            result = run("watch-feedback-once", "--briefing", self.briefing_id, "--room-ref", self.room_ref, "--origin-channel", "C123", "--origin-thread", "1.2", "--outbox", str(outbox), "--state-dir", str(self.state))
        finally:
            server.shutdown(); thread.join(); server.server_close()
        self.assertEqual(json.loads(result.stdout)["delivered"], 0)
        self.assertFalse(outbox.exists())


if __name__ == "__main__":
    unittest.main()
