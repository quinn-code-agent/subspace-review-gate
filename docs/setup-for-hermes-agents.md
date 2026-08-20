# Setup and self-use guide for Hermes agents

This guide is for a Hermes host that installs and operates `subspace-review-gate`. It covers local fixed-artifact review, optional temporary Human Review, and Relay-hosted Review Room ownership. It does not grant workflow controller authority.

Read [the README](../README.md) first for a product overview. Read [architecture.md](architecture.md) before changing authority, transport, or browser boundaries. The portable object contract is [Subspace Review & Gate v1](https://github.com/spacedock-dev/subspace-v0/blob/5e4a5f5cb7ce9521a3cc451aa9ec30ea4e6f1ddb/docs/review-and-gate.md).

## 1. What this host receives

```text
Hermes plugin
→ Subspace v1 Briefing and verification tools
→ Slack review/gate projection
→ optional Human Review runtime controls
→ optional Relay owner-client controls
```

The plugin can prepare review evidence and owner-side Relay operations. It does not make a browser reviewer, Slack, Relay, or the plugin itself a workflow writer.

## 2. Prerequisites

### Every host

| Need | Check |
|---|---|
| Hermes Agent | `hermes --version` |
| Python 3 | `python3 --version` |
| Local artifact access | `test -r ./artifact.md` |
| GitHub access to install/update the plugin | `gh auth status` or public HTTPS access |

### Temporary public Human Review

Use this only for a non-sensitive artifact and a deliberately temporary review URL.

| Need | Check |
|---|---|
| Node.js 20+ and npm | `node --version`, `npm --version` |
| `cloudflared` | `cloudflared --version` |
| `curl` | `curl --version` |
| npm global install permission or existing `human-review` | `command -v human-review` |

A Quick Tunnel is public and unauthenticated. Anyone holding its URL can read the artifact and submit feedback. Use a named Cloudflare Tunnel plus Cloudflare Access for durable or sensitive sharing; keep those credentials outside this plugin.

### Relay owner client

The plugin creates and retains a private owner receipt only after package publish. It stores owner receipts and Room records below:

```text
$HERMES_HOME/subspace-review-gate/relay/
```

These files contain credentials or capability material and must remain private. Do not copy them into a Briefing, Git, Slack, or a reviewer browser.

## 3. Install and confirm the plugin

```bash
hermes plugins install quinn-code-agent/subspace-review-gate
hermes plugins enable subspace-review-gate
hermes plugins list
```

Start a new Hermes session after enabling the plugin. It provides the `subspace_review_gate` toolset and the agent instruction file at:

```text
skills/subspace-review-gate/SKILL.md
```

An installed agent should load that skill when it needs a durable review or decision handoff for a fixed artifact. The skill also says when ordinary discussion should remain ordinary discussion.

## 4. Choose how this Hermes host will use the plugin

### Fixed-artifact review

Use this for a document, proposal, design preview, specification, or plan that is ready to be read by others.

1. Finish and render or otherwise verify the artifact.
2. Create a Briefing with one question, fixed SHA-256 artifact revision, and ordered routes.
3. Verify the Briefing immediately before sharing it.
4. Open a reviewer surface and render the matching Slack projection.
5. Treat feedback as evidence and an explicit route selection as a candidate Resolution.

For a local smoke test:

```bash
mkdir -p .review
printf '# Review smoke test\n\nThis is a fixed artifact.\n' > .review/smoke.md

subspace-review-gate create \
  --artifact .review/smoke.md \
  --question 'Is this review clear?' \
  --briefing .review/smoke-briefing.json \
  --route 'approve|Ready|review:ready' \
  --route 'revise|Describe what to change|review:revise'

subspace-review-gate verify --briefing .review/smoke-briefing.json
```

For a Spacedock-backed workflow, only the authorized controller or dispatched leg can apply a validated Resolution. For an independent artifact, keep the portable outcome beside the Briefing without inventing a workflow state change.

### Temporary Human Review

First check and, if needed, install the patched runtime:

```bash
subspace-review-runtime doctor
subspace-review-runtime install-runtime
```

Then open a non-sensitive artifact:

```bash
subspace-review-runtime open --artifact .review/smoke.md
```

The command prints a URL only after it verifies the public session shell. Run `human-review poll <artifact> --timeout …` while the review is open. A review surface is proven only when a feedback batch arrives, not when an HTTP request returns 200.

Close the temporary public surface when finished:

```bash
subspace-review-runtime close
```

### Relay-hosted Review Room owner client

Use this when Relay should host the browser review surface for an immutable Briefing. The Hermes plugin remains the owner client.

```text
verify Briefing
→ subspace_review_gate_relay_package
→ subspace_review_gate_relay_publish
→ private owner receipt
→ subspace_review_gate_relay_create_room
→ human deliberately delivers Room URL capability
→ Relay browser reviewer submits feedback-only Result
→ subspace_review_gate_relay_results
→ subspace_review_gate_relay_pull_result
```

The Room URL is a capability. The plugin does not print, post, fan out, or automatically deliver it. A Room is controlled through a private local `room_ref`:

- `subspace_review_gate_relay_create_room` creates a Room and returns a non-network `room_ref`.
- `subspace_review_gate_relay_results` returns safe owner-visible Result summaries.
- `subspace_review_gate_relay_pull_result` writes a verified feedback-mode Result locally and reports its digests.
- `subspace_review_gate_relay_disable_room` disables the Room.
- `subspace_review_gate_relay_revoke_room_session` revokes an arrived reviewer session without disabling sibling sessions, but requires an already supplied session ID.

Session IDs are not discoverable by this plugin. Do not guess, derive, log, or request them through a reviewer browser. Use the revoke control only when an owner already has a session ID through an approved Relay owner channel.

The browser receives no owner device secret, owner receipt, or workflow authority. Relay feedback remains evidence; it does not become a Resolution or workflow verdict automatically.

## 5. Agent self-use

The runtime guidance for an installed agent is [skills/subspace-review-gate/SKILL.md](../skills/subspace-review-gate/SKILL.md).

Use the system when a discussion has become a fixed artifact that needs review, asynchronous feedback, an explicit choice, or durable handoff. Do not open a Briefing for ordinary open-ended conversation. First write the short proposal, decision note, design, or plan that people can actually review.

## 6. Update and verify

```bash
hermes plugins update subspace-review-gate
python3 -m unittest discover -v "$HERMES_HOME/plugins/subspace-review-gate/tests"
```

If `$HERMES_HOME` is not set, Hermes normally uses `~/.hermes`. Do not hardcode that location in automation because profiles can set a different `HERMES_HOME`.

## 7. Troubleshooting

| Symptom | Meaning / action |
|---|---|
| `doctor` reports missing commands | Install the named dependency. Do not copy a URL or runtime state from another host. |
| public `open` refuses | Cloudflare did not provide a verifiable public Tunnel. No usable URL was created. Retry later or use named Tunnel + Access. |
| Quick Tunnel returns 502 | The local proxy or Human Review server stopped. Run `subspace-review-runtime status`, close stale state, and open a new session. |
| `poll` times out | No feedback batch arrived. It does not prove the browser path works. |
| Slack route is ambiguous | Rebuild the Resolution from an explicit route number or route ID. |
| Relay owner action refuses | Check the requested Briefing has its private owner receipt and that the operation is using the intended profile-local `$HERMES_HOME`. |

## 8. Safety checklist

- [ ] The artifact is appropriate for the chosen review surface.
- [ ] The Briefing SHA-256 verifies after the artifact was finalized.
- [ ] Temporary public review URLs are closed when no longer needed.
- [ ] Owner receipts, secrets, Room IDs, session values, and capability URLs stay out of Git, Slack, and reviewer output.
- [ ] Feedback is not treated as a workflow verdict.
- [ ] Any workflow change is separately made and evidenced by its authorized controller.
