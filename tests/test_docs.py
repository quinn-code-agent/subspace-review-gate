import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class DocumentationTests(unittest.TestCase):
    def test_setup_guide_has_reproducible_commands_and_safety_boundaries(self):
        text = (ROOT / "docs" / "setup-for-hermes-agents.md").read_text()
        for required in (
            "hermes plugins install quinn-code-agent/subspace-review-gate",
            "subspace-review-runtime doctor",
            "subspace-review-runtime install-runtime",
            "subspace-review-runtime open --artifact",
            "subspace-review-runtime close",
            "human-review poll",
            "Quick Tunnel is public",
            "workflow controller",
        ):
            self.assertIn(required, text)

    def test_setup_guide_covers_self_use_and_relay_owner_client(self):
        text = (ROOT / "docs" / "setup-for-hermes-agents.md").read_text()
        for required in (
            "## 4. Choose how this Hermes host will use the plugin",
            "### Fixed-artifact review",
            "### Relay-hosted Review Room owner client",
            "subspace_review_gate_relay_create_room",
            "subspace_review_gate_relay_pull_result",
            "Room URL is a capability",
            "skills/subspace-review-gate/SKILL.md",
        ):
            self.assertIn(required, text)

    def test_architecture_has_mermaid_and_single_writer_boundary(self):
        text = (ROOT / "docs" / "architecture.md").read_text()
        self.assertGreaterEqual(text.count("```mermaid"), 5)
        for required in (
            "Immutable Subspace v1 Briefing",
            "Human Review",
            "Slack",
            "workflow controller / dispatched leg",
            "Subspace Relay",
        ):
            self.assertIn(required, text)

    def test_architecture_describes_relay_as_owner_client_not_future_host(self):
        text = (ROOT / "docs" / "architecture.md").read_text()
        self.assertIn("Hermes owner client", text)
        self.assertIn("Room URL capability", text)
        self.assertIn("does not host a browser", text)
        self.assertNotIn("potential future **transport adapter**", text)

    def test_readme_explains_the_hermes_subspace_integration_in_plain_language(self):
        text = (ROOT / "README.md").read_text()
        for required in (
            "Hermes 的 Subspace Review & Gate v1 integration",
            "Hermes-native Subspace owner client",
            "Hermes 的 portable-review adapter",
            "not a new review format",
            "does not turn feedback into a workflow verdict",
        ):
            self.assertIn(required, text)

    def test_readme_documents_relay_room_owner_client_boundary(self):
        text = (ROOT / "README.md").read_text()
        for required in (
            "Room URL is a capability",
            "subspace_review_gate_relay_create_room",
            "subspace_review_gate_relay_pull_result",
            "does not host a browser",
            "does not create a Resolution",
            "revoke an arrived reviewer session",
        ):
            self.assertIn(required, text)
        self.assertNotIn("Relay-backed Subspace Web viewer", text)

    def test_readme_has_a_reader_path_for_product_operator_and_agent(self):
        text = (ROOT / "README.md").read_text()
        for required in (
            "## Choose a path",
            "## Where to read next",
            "### Review a fixed artifact",
            "### Run a Relay-hosted Review Room",
            "docs/setup-for-hermes-agents.md",
            "docs/architecture.md",
            "skills/subspace-review-gate/SKILL.md",
        ):
            self.assertIn(required, text)

    def test_readme_links_both_new_documents(self):
        text = (ROOT / "README.md").read_text()
        self.assertIn("docs/setup-for-hermes-agents.md", text)
        self.assertIn("docs/architecture.md", text)


if __name__ == "__main__":
    unittest.main()
