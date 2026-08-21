# Subspace Review & Gate for Hermes

`subspace-review-gate` lets a Hermes session use the portable [Subspace Review & Gate v1](https://github.com/spacedock-dev/subspace-v0/blob/5e4a5f5cb7ce9521a3cc451aa9ec30ea4e6f1ddb/docs/review-and-gate.md) contract for fixed documents, designs, proposals, specifications, and plans.

## What this plugin is

This plugin brings the Subspace Review & Gate v1 contract into Hermes. It uses the same `Briefing`, `Annotation`, and feedback Result objects as other Subspace clients; it is not a new review format.

Three names describe the same role:

- **Hermes 的 Subspace Review & Gate v1 integration**: Hermes can create, verify, package, and recover portable review objects.
- **Hermes-native Subspace owner client**: a Hermes owner can publish a package, operate a Relay Review Room, and pull feedback through private owner credentials.
- **Hermes 的 portable-review adapter**: one fixed review contract can move between Hermes, Relay, browser viewers, Human Review, and Slack without changing format at each step.

Relay stores and delivers bytes. A browser viewer collects feedback. The plugin handles the owner side. None of these pieces decides whether work is approved or writes a workflow status: the plugin does not turn feedback into a workflow verdict.

## Choose a path

### Review a fixed artifact

Use this when people or agents need to read the same fixed version of a document, design, proposal, or plan.

```text
artifact bytes
→ Briefing with a SHA-256 revision and one question
→ Human Review or another reviewer surface
→ feedback annotations
→ an explicit Slack route choice, when a decision is needed
```

Use the plugin's Briefing, verification, Slack-rendering, and Resolution-building tools. Human Review comments are evidence. Slack replies are candidate choices. A workflow controller decides whether a validated Resolution changes any workflow state.

### Run a Relay-hosted Review Room

Use this when a Hermes owner needs Relay to host the browser review surface for one immutable Briefing.

```text
verify and publish package
→ private owner receipt
→ create Room
→ a human deliberately delivers the Room URL capability
→ Relay browser session submits feedback-only Result
→ owner lists and pulls the Result
```

The plugin is the owner client. Relay owns the Room, browser session, cookie/CSRF boundary, and immutable Result storage. Start with `subspace_review_gate_relay_package` and `subspace_review_gate_relay_publish`, then create the Room. The **Room URL is a capability**, not a status link. The plugin does not host a browser. It does not create a Resolution or automatically deliver a Room URL.

Owner controls are `subspace_review_gate_relay_create_room`, `subspace_review_gate_relay_results`, `subspace_review_gate_relay_owner_inbox`, `subspace_review_gate_relay_pull_result`, `subspace_review_gate_relay_disable_room`, and `subspace_review_gate_relay_revoke_room_session`. A private `room_ref` can disable a Room. The plugin can revoke an arrived reviewer session only when an already supplied session ID is available; session IDs are not discoverable by this plugin.

`relay_results` is agent-facing and returns structural metadata only: Result id, opaque participant correlation token, and whether self-declared attribution exists. It never returns reviewer labels or feedback text. `relay_owner_inbox` is the separate human-facing path: it validates the local package and pulled feedback, then writes one private `0600`, self-contained, script-free HTML snapshot such as `owner-inbox.html` with escaped and length-capped reviewer labels and annotations. The HTML marks attribution as self-declared and unverified. It is a local snapshot, not a browser server, and it does not enable reviewer shared feedback.

### Legacy local Relay Web viewer

`bin/subspace-relay-web` is an optional local development viewer for a published Briefing. It is not a Relay Room host and must not be used to distribute a Room or share capability. It binds to `127.0.0.1` by default.

## What this plugin does not do

- It does not replace the Subspace v1 contract or create a second review schema.
- It does not make self-declared reviewer attribution into verified identity or workflow authority.
- It does not let Slack, Human Review, Relay, or a browser viewer write a workflow verdict.
- It does not automatically expose owner credentials, owner receipts, browser session values, Result envelopes, or capability URLs.

## Install

```bash
hermes plugins install quinn-code-agent/subspace-review-gate
hermes plugins enable subspace-review-gate
```

Start a new Hermes session after enabling the plugin. It registers the `subspace_review_gate` toolset and installs the `subspace-review-gate` skill.

## Quick start

Create a complete artifact first. Then create and verify one immutable Briefing:

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

A Briefing fixes one question, its artifact revision, and its routes. If any of those change, create a new Briefing instead of editing the existing one.

Render the matching Slack companion only after verification:

```bash
subspace-review-gate render-slack \
  --briefing ./.review/briefing-readme-r1.json \
  --human-review-url 'http://100.x.y.z:17891/s/s_example'
```

Use `build-resolution` only for an explicit route choice. `revise` and `hold` need a reason or included feedback evidence:

```bash
subspace-review-gate build-resolution \
  --briefing ./.review/briefing-readme-r1.json \
  --choice 2 \
  --reason 'Add a concrete example before publication.'
```

A Slack review message must include the Briefing ID, question, fixed revision, reviewer link, ordered routes, and `Reply with the option number`. A comment, question, or emoji remains advisory.

## Where to read next

- [Setup for Hermes agents](docs/setup-for-hermes-agents.md): self-installation, dependencies, smoke tests, and safe operation of the Human Review runtime and Relay owner client.
- [Architecture](docs/architecture.md): the authority boundary between the plugin, Relay, browser reviewers, and workflow controllers.
- [Agent skill](skills/subspace-review-gate/SKILL.md): when an installed Hermes agent should create a fixed artifact, open a review, or keep a discussion as ordinary conversation.
- [Subspace Review & Gate v1](https://github.com/spacedock-dev/subspace-v0/blob/5e4a5f5cb7ce9521a3cc451aa9ec30ea4e6f1ddb/docs/review-and-gate.md): portable object meanings and invariants.

## Development

```bash
python3 -m unittest discover -s tests -v
```

The suite covers Briefing identity, route validation, Relay owner boundaries, runtime behavior, documentation claims, and the local reviewer shell.

## License

MIT
