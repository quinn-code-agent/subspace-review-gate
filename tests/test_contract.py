import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
CLI = ROOT / "bin" / "subspace-review-gate"


def run(*args, check=True):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=True,
    )


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name)
        self.artifact = self.path / "proposal.md"
        self.briefing = self.path / "briefing.json"

    def tearDown(self):
        self.tempdir.cleanup()

    def create(self, *routes):
        self.artifact.write_bytes(b"# Proposal\n\nShip the small thing.\n")
        args = ["create", "--artifact", str(self.artifact), "--question", "Accept this proposal?", "--briefing", str(self.briefing)]
        for route in routes:
            args.extend(["--route", route])
        return run(*args)

    def test_create_emits_v1_briefing_with_raw_sha256(self):
        result = self.create(
            "approve|Use it|stage:planning",
            "revise|Change it|stage:draft",
            "hold|Park it|tasking:park",
        )
        data = json.loads(self.briefing.read_text())
        self.assertEqual(Path(result.stdout.strip()).resolve(), self.briefing.resolve())
        self.assertEqual(data["type"], "Briefing")
        self.assertEqual(data["version"], "1")
        self.assertEqual(data["artifacts"][0]["rev"], "sha256:" + hashlib.sha256(self.artifact.read_bytes()).hexdigest())
        self.assertEqual([route["decision"] for route in data["context"][0]["routes"]], ["approve", "revise", "hold"])

    def test_verify_detects_changed_artifact(self):
        self.create()
        self.artifact.write_text("new\n")
        result = run("verify", "--briefing", str(self.briefing), check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("digest mismatch", result.stderr)

    def test_render_slack_preserves_ordered_routes_and_reply_instruction(self):
        self.create("approve|Plan|stage:planning", "revise|Revise|stage:draft")
        result = run("render-slack", "--briefing", str(self.briefing), "--human-review-url", "http://tailnet/s/session")
        self.assertIn("1. *Plan* — approve → `stage:planning`", result.stdout)
        self.assertIn("2. *Revise* — revise → `stage:draft`", result.stdout)
        self.assertIn("Reply with the option number", result.stdout)
        self.assertIn("*Human Review:* http://tailnet/s/session", result.stdout)

    def test_build_resolution_refuses_ambiguous_and_requires_reason_for_revise(self):
        self.create("approve|Plan|stage:planning", "revise|Revise|stage:draft")
        missing_reason = run("build-resolution", "--briefing", str(self.briefing), "--choice", "2", check=False)
        ambiguous = run("build-resolution", "--briefing", str(self.briefing), "--choice", "approve revise", check=False)
        self.assertEqual(missing_reason.returncode, 2)
        self.assertIn("requires --reason", missing_reason.stderr)
        self.assertEqual(ambiguous.returncode, 2)
        self.assertIn("does not match exactly one route", ambiguous.stderr)

    def test_build_resolution_emits_annotation_and_resolution(self):
        self.create("revise|Revise copy|stage:draft")
        result = run("build-resolution", "--briefing", str(self.briefing), "--choice", "1", "--reason", "Clarify scope")
        data = json.loads(result.stdout)
        self.assertEqual(data["outcome"], "resolved")
        self.assertEqual(data["route"]["decision"], "revise")
        self.assertEqual(data["annotation"]["target"], data["route"]["id"])
        self.assertEqual(data["resolution"]["reason"], "Clarify scope")


if __name__ == "__main__":
    unittest.main()
