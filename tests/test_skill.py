import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "subspace-review-gate" / "SKILL.md"


class SubspaceReviewGateSkillTests(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text()
        match = re.match(r"\A---\n(?P<frontmatter>.*?)\n---\n(?P<body>.+)\Z", self.text, re.DOTALL)
        if match is None:
            self.fail("SKILL.md must begin with YAML frontmatter")
        self.frontmatter = match.group("frontmatter")
        self.body = match.group("body")

    def test_frontmatter_has_shippable_hermes_skill_fields(self):
        for required in (
            "name: subspace-review-gate",
            "description:",
            "version:",
            "author:",
            "license: MIT",
            "compatibility:",
            "platforms: [linux, macos, windows]",
            "metadata:",
            "  hermes:",
            "    tags:",
            "    related_skills:",
        ):
            self.assertIn(required, self.frontmatter)
        description = re.search(r'^description: "?(.+?)"?$', self.frontmatter, re.MULTILINE)
        if description is None:
            self.fail("frontmatter must include description")
        self.assertLessEqual(len(description.group(1)), 60)
        self.assertIn("Subspace", description.group(1))
        self.assertTrue(description.group(1).endswith("."))

    def test_trigger_includes_durable_handoff_and_ordinary_discussion_counter_trigger(self):
        for required in (
            "## When to Use",
            "asynchronous feedback",
            "durable handoff",
            "Do not use this skill for ordinary open-ended conversation.",
            "fixed artifact",
        ):
            self.assertIn(required, self.body)

    def test_procedure_preserves_immutable_and_single_writer_boundaries(self):
        for required in (
            "## Procedure",
            "subspace_review_gate_create",
            "subspace_review_gate_verify",
            "subspace_review_gate_build_resolution",
            "workflow controller or dispatched leg",
            "## Pitfalls",
            "## Verification",
            "[Q]",
            "[RES]",
        ):
            self.assertIn(required, self.body)
        self.assertNotIn("/Users/", self.text)


if __name__ == "__main__":
    unittest.main()
