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
        ])
        self.assertTrue(all(entry["toolset"] == "subspace_review_gate" for entry in ctx.tools))

    def test_plugin_returns_json_error_for_missing_briefing(self):
        result = json.loads(PLUGIN.verify({"briefing": "/definitely/missing.json"}))
        self.assertFalse(result["ok"])
        self.assertIn("invalid Briefing", result["error"])


if __name__ == "__main__":
    unittest.main()
