# Setup guide for Hermes agents

This guide lets a new Hermes host reproduce the current Subspace Review & Gate flow for a fixed artifact: an immutable Subspace v1 Briefing, a review viewer, a Slack gate projection, and a portable Resolution. It does not grant workflow-controller authority.

Read [`architecture.md`](architecture.md) first for the responsibility boundaries. The governing review transport contract is [Subspace Review & Gate v1](https://github.com/spacedock-dev/subspace-v0/blob/5e4a5f5cb7ce9521a3cc451aa9ec30ea4e6f1ddb/docs/review-and-gate.md).

## 1. What this installs

```text
artifact → Briefing + SHA-256 → Human Review feedback → Slack route selection
         → validated Annotation + Resolution → controller leg, if a workflow exists
```

The plugin supplies the Briefing/digest/Resolution tools and an optional public Human Review runtime. It does **not** make Slack or the reviewer viewer a workflow writer.

## 2. Required capabilities

### Required for every host

| Need | Why | Check |
|---|---|---|
| Hermes Agent | plugin host and tool registry | `hermes --version` |
| Python 3 | plugin CLI and tests | `python3 --version` |
| GitHub read access | install/update the plugin repository | `gh auth status` or public HTTPS access |
| Local artifact access | raw bytes are hashed and reviewed locally | `test -r ./artifact.md` |

### Required for the temporary public review viewer

| Need | Why | Check |
|---|---|---|
| Node.js 20+ and npm | Human Review viewer | `node --version`, `npm --version` |
| `cloudflared` | temporary HTTPS Quick Tunnel | `cloudflared --version` |
| `curl` | public-session verification | `curl --version` |
| npm global-install permission, or preinstalled `human-review` | installs the remote-origin-safe Human Review fork | `command -v human-review` |
| Outbound HTTPS / QUIC to Cloudflare | creates and serves the Quick Tunnel | run `subspace-review-runtime doctor` |

No Cloudflare account, own DNS, Tailscale, or API key is needed for a temporary Quick Tunnel. A Quick Tunnel is public and unauthenticated: anyone who receives its capability URL can read the artifact and submit feedback.

### Required for durable or sensitive sharing

Use a named Cloudflare Tunnel plus Cloudflare Access instead of a Quick Tunnel. That requires a Cloudflare account, a controlled hostname/DNS zone, Access policy, and credentials managed outside this plugin. Do not put those credentials in a Briefing, repository, or Slack message.

## 3. Install the plugin

```bash
hermes plugins install quinn-code-agent/subspace-review-gate
hermes plugins enable subspace-review-gate
```

Start a new Hermes session after enabling it. Confirm the plugin is enabled:

```bash
hermes plugins list
```

The installed plugin also supplies the `subspace-review-gate` skill. In an agent session, load that skill before opening an artifact review.

## 4. Prepare the optional Human Review runtime

Run a machine-readable prerequisite check:

```bash
subspace-review-runtime doctor
```

If `human-review` is missing, install the patched fork:

```bash
subspace-review-runtime install-runtime
```

The fork is [`quinn-code-agent/human-review`](https://github.com/quinn-code-agent/human-review). It is required for remote review because the stock viewer can point the artifact iframe at the reviewer's own loopback address. The fork preserves a reachable proxied/public origin while retaining loopback isolation for a local session.

## 5. First smoke test

Use a non-sensitive Markdown file for the first external test.

```bash
mkdir -p .review
printf '# Review smoke test\n\nThis is a fixed artifact.\n' > .review/smoke.md

subspace-review-gate create \
  --artifact .review/smoke.md \
  --question 'Is the review transport working?' \
  --briefing .review/smoke-briefing.json \
  --route 'approve|Transport verified|review:verified' \
  --route 'revise|Describe the observed problem|review:revise'

subspace-review-gate verify --briefing .review/smoke-briefing.json
subspace-review-runtime open --artifact .review/smoke.md
```

`open` only prints a URL after it verifies that the public URL returns the exact expected Human Review session. It stores process state at:

```text
$HERMES_HOME/subspace-review-gate/public-review.json
```

If Cloudflare allocates a Quick Tunnel hostname that cannot be resolved yet, the runtime does not return it. It stops that tunnel and retries; a final refusal is safer than a broken link.

In a separate terminal, receive feedback:

```bash
human-review poll .review/smoke.md --timeout 1800
```

Open the returned URL from another network/browser, add a short note, and click **Send**. The smoke test passes only if `poll` receives a feedback batch. HTTP 200 alone does not prove the reviewer can view and submit.

Close the public surface when done:

```bash
subspace-review-runtime close
```

## 6. Run an actual artifact review

1. Finish and locally verify the artifact before sharing it.
2. Create a new Briefing with one decision question and ordered routes.
3. Verify its raw-byte SHA-256 immediately before publishing.
4. Open Human Review with `subspace_review_gate_open_public_review` or `subspace-review-runtime open`.
5. Render the matching Slack surface with `subspace_review_gate_render_slack` or the CLI.
6. Post Briefing ID, question, fixed revision, review URL, routes in order, and **Reply with the option number**.
7. Treat Human Review edits/comments as advisory evidence. Treat Slack replies as candidate Resolutions.
8. Run `subspace_review_gate_build_resolution` against the immutable Briefing. It refuses ambiguous choice text and requires rationale for `revise` and `hold`.
9. Only an authorized workflow controller or dispatched leg may apply a binding Resolution to a Spacedock entity.

For an artifact with no workflow, persist the validated Annotation/Resolution next to its Briefing and report the outcome; do not fabricate a status transition.

## 7. Update and verify the installation

```bash
hermes plugins update subspace-review-gate
python3 -m unittest discover -v "$HERMES_HOME/plugins/subspace-review-gate/tests"
```

If `$HERMES_HOME` is not set, Hermes normally uses `~/.hermes`. Do not hardcode that path in automation: profiles can set a different `HERMES_HOME`.

## 8. Troubleshooting

| Symptom | Meaning / action |
|---|---|
| `doctor` reports missing commands | Install the named missing dependency; do not bypass it with a URL copied from another host. |
| `open` refuses after tunnel attempts | Cloudflare did not provide a publicly resolvable and verified Quick Tunnel. No usable URL was produced. Retry later or use named Tunnel + Access. |
| Quick Tunnel gives HTTP 502 | The local proxy or Human Review server stopped. Run `subspace-review-runtime status`; close stale state and reopen. |
| Viewer says session ended | A Human Review session is memory-resident. Reopen a new review URL; do not reuse an old session URL. |
| Viewer shows blank / loopback error remotely | Confirm the patched `quinn-code-agent/human-review` fork is installed, not stock Human Review. |
| `poll` times out | No feedback batch was sent. It is not evidence that the viewer works or fails; keep polling or ask the reviewer to click Send. |
| Slack link includes a trailing `*` or `)` | Post the URL as a plain link without wrapping punctuation/formatting. |
| Slack says `approve` but route is unclear | Do not infer. Rebuild the Resolution from the explicit route number or ID. |

## 9. Security checklist

- [ ] Artifact is safe for a public unauthenticated capability URL, or a protected named tunnel is in use.
- [ ] Briefing SHA-256 verifies after artifact rendering/generation.
- [ ] Quick Tunnel is closed after review.
- [ ] Secrets, access tokens, device credentials, and server records are excluded from artifact, Briefing, Git, and Slack.
- [ ] Human Review feedback is not treated as a workflow verdict.
- [ ] Slack resolution is validated against the exact Briefing route before any workflow leg receives it.
