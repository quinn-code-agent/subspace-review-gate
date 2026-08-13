# Subspace Review & Gate for Hermes

A standalone Hermes plugin for reviewing fixed artifacts—documents, proposals, designs, specifications, and plans—through the portable [Subspace Review & Gate v1](https://github.com/spacedock-dev/subspace-v0/blob/5e4a5f5cb7ce9521a3cc451aa9ec30ea4e6f1ddb/docs/review-and-gate.md) contract.

It makes one contract visible in two complementary review surfaces:

- **Human Review** renders the artifact and receives anchored comments, direct edits, and overall feedback.
- **Slack** presents the same immutable Briefing, ordered routing choices, and a reply-by-number gate UI.

This plugin does **not** execute workflows. For Spacedock-backed work, the First Officer or a dispatched leg remains the only writer of a verdict. For independent artifacts, the result is stored as portable Review & Gate entries beside the Briefing.

## Contract-first flow

```text
fixed artifact bytes
  → immutable Subspace v1 Briefing (artifact URI + sha256 + routes)
  → verify raw-byte digest
  → Human Review projection (comments / edits)
  → Slack projection (ordered routes / reply-by-number)
  → validated Annotation + Resolution
  → workflow controller applies routing, if one exists
```

A Briefing is one decision opportunity. Change the artifact revision, question, or routes and create a new Briefing; never mutate the old one.

## Install

```bash
hermes plugins install quinn-code-agent/subspace-review-gate
hermes plugins enable subspace-review-gate
```

Restart a new Hermes session after enabling it. The plugin registers the `subspace_review_gate` toolset and installs the `subspace-review-gate` skill.

## Quick start

Create an artifact first, then create a Briefing:

```bash
subspace-review-gate create \
  --artifact ./README.md \
  --question "Is this README ready to publish?" \
  --briefing ./.review/briefing-readme-r1.json \
  --route 'approve|Publish this README|publication:ready' \
  --route 'revise|Revise the README|authoring:revise' \
  --route 'hold|Park publication|tasking:park'

subspace-review-gate verify --briefing ./.review/briefing-readme-r1.json
```

The generated Briefing contains fixed raw-byte `sha256:` revisions. Do not hand-edit it after sharing.

Open the artifact in the patched Human Review fork, then render a Slack companion message:

```bash
subspace-review-gate render-slack \
  --briefing ./.review/briefing-readme-r1.json \
  --human-review-url 'http://100.x.y.z:17891/s/s_example'
```

A reviewer may leave detailed comments in Human Review, then select a Slack route. Convert a selected option into contract entries:

```bash
subspace-review-gate build-resolution \
  --briefing ./.review/briefing-readme-r1.json \
  --choice 2 \
  --reason 'Add a concrete example before publication.'
```

`revise` and `hold` require a reason or a prior included Annotation. `approve` still preserves the exact chosen route and its destination—decision alone is not routing.

## External Human Review

The stock Human Review client assumes a local browser and changes the artifact iframe to `127.0.0.1` for non-loopback origins. Use the companion fork at [quinn-code-agent/human-review](https://github.com/quinn-code-agent/human-review), which retains the reachable remote origin for Tailnet or reverse-proxied reviews while preserving loopback isolation locally.

For temporary internal review:

- run Human Review on the artifact;
- expose it only on the Tailnet IP using a proxy that rewrites the upstream Host header to loopback;
- leave `human-review poll <artifact> --timeout …` running;
- verify a test feedback submission actually reaches the poll.

For durable access, use a named authenticated tunnel. Do not expose sensitive artifacts through a public unauthenticated Quick Tunnel.

## Slack gate UI

Slack is a projection, not the portable log or workflow writer. The posted message must show:

1. Briefing ID and question;
2. fixed artifact revision;
3. Human Review link;
4. ordered routing options exactly as in `Routing.routes`;
5. a clear reply-by-number instruction.

Use a Slack native control only if it selects one explicit route ID. Treat all comments, questions, emoji acknowledgements, and ambiguous responses as advisory. A binding Resolution requires an externally authorized approver and must be applied by the owning workflow controller.

## Development

```bash
python3 -m unittest -v tests/test_contract.py
```

The suite verifies Briefing SHA-256 generation, digest mismatch rejection, stable Slack route ordering, and Resolution rationale/ambiguity rules.

## License

MIT
