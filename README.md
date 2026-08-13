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

For a clean Hermes host, follow the [setup guide for Hermes agents](docs/setup-for-hermes-agents.md). For the authority boundaries, runtime topology, and Mermaid diagrams, read [architecture](docs/architecture.md).

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

## External Human Review runtime

The plugin now manages the tested temporary public-review path. It uses the patched [quinn-code-agent/human-review](https://github.com/quinn-code-agent/human-review) fork: stock Human Review redirects a remote viewer's artifact iframe to its own `127.0.0.1`; the fork preserves the reachable external origin while keeping local loopback isolation.

### Prerequisites

A new Hermes host needs only:

1. Hermes Agent with this plugin installed and enabled;
2. Python 3 and Node.js 20+ (`node`, `npm`);
3. `cloudflared` on `PATH` with outbound access to Cloudflare;
4. permission to install the public Human Review fork globally through npm, or a preinstalled `human-review` command;
5. the local artifact to review.

No Cloudflare account, DNS setup, Tailscale, or API key is required for a **temporary public Quick Tunnel**. Check readiness:

```bash
subspace-review-runtime doctor
```

Install the patched viewer if missing:

```bash
subspace-review-runtime install-runtime
```

Open a verified public HTTPS viewer:

```bash
subspace-review-runtime open --artifact ./README.md
```

The command stores process state under `$HERMES_HOME/subspace-review-gate/`, creates the Human Review session, starts the loopback Host-rewriting proxy and Cloudflare Quick Tunnel, then verifies the exact public session URL returns the expected session shell. It prints the URL only after that verification.

Inspect or close it:

```bash
subspace-review-runtime status
subspace-review-runtime close
```

The corresponding Hermes tools are `subspace_review_gate_open_public_review`, `subspace_review_gate_review_status`, and `subspace_review_gate_close_public_review`.

A Quick Tunnel is public, temporary, and unauthenticated: anyone with the URL can submit feedback. Keep `human-review poll <artifact> --timeout …` running while review is open, and verify a submitted test feedback batch arrives before treating the viewer as usable. For durable or sensitive review, use a named authenticated Cloudflare Tunnel + Access; that requires a Cloudflare account, owned domain/DNS, and Access policy.

## Relay staging dogfood — Phase 1 feedback transport

Phase 1 adds a Relay-compatible, feedback-only adapter. It intentionally does **not** create a Resolution, interpret routing, or write a workflow verdict.

1. Create a Briefing with a portable relative artifact URI (the CLI now defaults to the artifact filename):

```bash
subspace-review-gate create --artifact ./README.md --artifact-uri README.md \
  --question 'Is this README clear?' --briefing .review/briefing.json \
  --route 'approve|Ready|publication:ready' \
  --route 'revise|Revise|authoring:revise'
subspace-review-gate verify --briefing .review/briefing.json
```

2. Produce and publish the exact immutable Relay package to the existing staging endpoint:

```bash
subspace-review-relay package --briefing .review/briefing.json --output-dir .review/relay-package
subspace-review-relay publish --package .review/relay-package
```

Relay independently verifies the manifest, artifact size, URI containment, raw SHA-256 digests, and Briefing/package coherence. The publish command retains an owner receipt under `$HERMES_HOME/subspace-review-gate/relay/owners/` with mode `0600`; it never prints the device secret.

3. A Web or TUI reviewer fetches and verifies the staging snapshot before rendering it:

```bash
subspace-review-relay fetch --briefing briefing:<32-lowercase-hex> --output-dir .review/fetched
```

4. Preserve Human Review as the Web feedback renderer. Convert a submitted Human Review batch to portable Subspace Annotation JSONL; this requires the externally confirmed reviewer identity and emits **no Resolution**:

```bash
subspace-review-relay annotations \
  --briefing .review/briefing.json \
  --feedback human-review-feedback.json \
  --reviewer person:reviewer \
  --output .review/review.jsonl
```

The four corresponding Hermes tools are `subspace_review_gate_relay_package`, `subspace_review_gate_relay_publish`, `subspace_review_gate_relay_fetch`, and `subspace_review_gate_relay_annotations`.

Relay share URLs are bearer capabilities: do not publish sensitive artifact bytes. Stage data is separate from production data but is real remote storage and uses real Relay quotas.

## Phase 2 — Relay-backed Subspace Web viewer

`bin/subspace-relay-web` is the replacement direction for Human Review's **transport**. It retains the browser interaction shell—rendered artifact, text selection, comment composition, and Send—but it owns no review protocol.

```text
Relay fetch + digest verification
→ browser interaction
→ Subspace Annotation JSONL
→ feedback-only Review v1 Result
→ Relay Result submission
→ owner-only Result pull
```

Start a local web shell for a published Briefing:

```bash
python3 bin/subspace-relay-web open \
  --briefing briefing:<32-lowercase-hex> \
  --reviewer person:<reviewer> \
  --no-browser
```

The shell fetches and verifies the Relay package before rendering. `Send` creates only `Annotation` entries and a `review-v1-result` with `mode: "feedback"`; it contains no `Resolution` and cannot route a workflow. The reviewer transport receipt is private local state. Owners inspect/pull Relay feedback through their private owner receipt:

```bash
bin/subspace-review-relay results --briefing briefing:<id>
bin/subspace-review-relay pull-result \
  --briefing briefing:<id> --result-id res_<id> --output-dir ./result
```

### Why this is not the old Human Review protocol

The old path was `Human Review feedback JSON → adapter → Annotation`. Phase 2's Web shell directly writes the Subspace objects and submits their verbatim bytes to Relay. Human Review-specific session, polling, batch, and acknowledgement semantics are absent from the Phase 2 viewer.

**Safety boundary:** Relay accepts and stores Result bytes; it does not interpret route semantics, authorize an approver, mint a binding Resolution, or modify workflow state. Slack remains a separately projected gate UI; an authorized external controller/leg remains the only workflow writer.

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
