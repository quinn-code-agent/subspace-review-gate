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

The plugin is the owner client. Relay owns the Room, browser session, cookie/CSRF boundary, and immutable Result storage. The **Room URL is a capability**, not a status link. The plugin does not host a browser and does not create a Resolution.

`subspace_review_gate_relay_share_consented` is the high-level clear-Yes path. It requires the disclosed artifact revision, audience, media type, and non-sensitive classification; checks Relay's actual capability limits; then creates, verifies, packages, publishes, and creates the Room. It returns only the validated Room URL and Relay's authoritative `expiresAt`. Unknown capabilities, changed bytes, ambiguous consent, unsupported media, malformed responses, or sensitivity refuse with no shareable URL.

`subspace_review_gate_relay_watch_feedback` starts a Room-scoped background watcher so Slack foreground handling does not block. The watcher owner-pulls exact bytes, validates the Result ID, Room, Briefing, feedback-only mode, artifact identity, and server digests, then emits one safe advisory event to the dispatch-bound origin-thread outbox. Its private cursor survives restart and deduplicates Result IDs. Feedback never advances workflow state. It stops when the Room is disabled, the Briefing expires, the user requests stop, or optional first-valid-feedback mode succeeds.

Lower-level owner controls remain available: `subspace_review_gate_relay_package`, `subspace_review_gate_relay_publish`, `subspace_review_gate_relay_create_room`, `subspace_review_gate_relay_results`, `subspace_review_gate_relay_pull_result`, `subspace_review_gate_relay_disable_room`, and `subspace_review_gate_relay_revoke_room_session`. A private `room_ref` can disable a Room. The plugin can revoke an arrived reviewer session only when an already supplied session ID is available; session IDs are not discoverable by this plugin.

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

The suite covers Briefing identity, route validation, Relay owner boundaries, consent and watcher behavior, runtime behavior, and documentation claims.

## License

MIT
