import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("review_gate_plugin", ROOT / "__init__.py")
assert SPEC is not None and SPEC.loader is not None
PLUGIN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLUGIN)


class Context:
    def __init__(self):
        self.tools = []

    def register_tool(self, **kwargs):
        self.tools.append(kwargs)


class PluginRegistrationTests(unittest.TestCase):
    def test_plugin_registers_bounded_contract_tools(self):
        ctx = Context()
        PLUGIN.register(ctx)
        self.assertEqual([entry["name"] for entry in ctx.tools], [
            "subspace_review_gate_create",
            "subspace_review_gate_verify",
            "subspace_review_gate_render_slack",
            "subspace_review_gate_build_resolution",
            "subspace_review_gate_open_public_review",
            "subspace_review_gate_review_status",
            "subspace_review_gate_close_public_review",
            "subspace_review_gate_relay_package",
            "subspace_review_gate_relay_publish",
            "subspace_review_gate_relay_fetch",
            "subspace_review_gate_relay_annotations",
            "subspace_review_gate_relay_results",
            "subspace_review_gate_relay_pull_result",
            "subspace_review_gate_relay_create_room",
            "subspace_review_gate_relay_disable_room",
            "subspace_review_gate_relay_revoke_room_session",
            "subspace_review_gate_relay_share_consented",
            "subspace_review_gate_relay_watch_feedback",
            "subspace_review_gate_relay_stop_feedback_watch",
        ])
        self.assertTrue(all(entry["toolset"] == "subspace_review_gate" for entry in ctx.tools))

    def test_plugin_exposes_owner_result_pull_with_private_state(self):
        ctx = Context()
        PLUGIN.register(ctx)
        entry = next(tool for tool in ctx.tools if tool["name"] == "subspace_review_gate_relay_pull_result")
        parameters = entry["schema"]["parameters"]
        self.assertEqual(parameters["required"], ["briefing", "result_id", "output_dir"])
        self.assertIn("state_dir", parameters["properties"])
        self.assertIn("feedback-only", entry["schema"]["description"])

    def test_room_controls_require_non_network_room_ref(self):
        ctx = Context()
        PLUGIN.register(ctx)
        for name, required in (
            ("subspace_review_gate_relay_disable_room", ["briefing", "room_ref"]),
            ("subspace_review_gate_relay_revoke_room_session", ["briefing", "room_ref", "session_id"]),
        ):
            entry = next(tool for tool in ctx.tools if tool["name"] == name)
            parameters = entry["schema"]["parameters"]
            self.assertEqual(parameters["required"], required)
            self.assertIn("room_ref", parameters["properties"])
            self.assertNotIn("room_id", parameters["properties"])

    def test_plugin_manifest_declares_every_relay_owner_tool(self):
        tools = (ROOT / "plugin.yaml").read_text()
        for name in (
            "subspace_review_gate_relay_results",
            "subspace_review_gate_relay_pull_result",
            "subspace_review_gate_relay_create_room",
            "subspace_review_gate_relay_disable_room",
            "subspace_review_gate_relay_revoke_room_session",
            "subspace_review_gate_relay_share_consented",
            "subspace_review_gate_relay_watch_feedback",
            "subspace_review_gate_relay_stop_feedback_watch",
        ):
            self.assertIn(name, tools)

    def test_high_level_share_requires_consent_bound_revision_and_disclosures(self):
        ctx = Context()
        PLUGIN.register(ctx)
        entry = next(tool for tool in ctx.tools if tool["name"] == "subspace_review_gate_relay_share_consented")
        required = entry["schema"]["parameters"]["required"]
        for field in ("artifact", "question", "consent", "consented_revision", "audience", "media_type", "sensitivity", "briefing", "package", "state_dir"):
            self.assertIn(field, required)
        self.assertIn("returns only", entry["schema"]["description"])

    def test_background_watcher_binds_origin_and_never_claims_workflow_authority(self):
        ctx = Context()
        PLUGIN.register(ctx)
        entry = next(tool for tool in ctx.tools if tool["name"] == "subspace_review_gate_relay_watch_feedback")
        required = entry["schema"]["parameters"]["required"]
        self.assertEqual(required, ["briefing", "room_ref", "origin_channel", "origin_thread", "outbox", "state_dir"])
        self.assertIn("background", entry["schema"]["description"])
        self.assertIn("does not advance", entry["schema"]["description"])

    def test_plugin_returns_json_error_for_missing_briefing(self):
        result = json.loads(PLUGIN.verify({"briefing": "/definitely/missing.json"}))
        self.assertFalse(result["ok"])
        self.assertIn("invalid Briefing", result["error"])


if __name__ == "__main__":
    unittest.main()
