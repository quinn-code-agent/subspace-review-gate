---
name: subspace-review-gate
description: Review fixed artifacts through Subspace v1 and Human Review.
license: MIT
compatibility: Requires the subspace-review-gate Hermes plugin and a local Human Review server for interactive review.
metadata:
  author: Kent
  contract: Subspace Review & Gate v1
---

# Subspace Review & Gate

Use this skill whenever a user needs review of a fixed artifact: a README, document, design preview, proposal, specification, or implementation plan. The portable Subspace v1 Briefing is the only contract that crosses workflow, Slack, and reviewer surfaces. Human Review is a projection surface; Slack is a compact decision UI. Neither directly mutates a workflow.

## Procedure

1. Create the complete artifact and render or otherwise verify it before review. Do not open a review on a draft that has not been checked.
2. Use `subspace_review_gate_create` to write an immutable v1 Briefing. Include the exact artifact, its raw-byte SHA-256 revision, one question, and ordered routes. A Spacedock entity may supply routing context but is not required.
3. Use `subspace_review_gate_verify` immediately before publishing. A digest mismatch requires a new Briefing; never overwrite the old revision.
4. Open the artifact in Human Review. For a public temporary reviewer URL, use `subspace_review_gate_open_public_review`; it requires Node, the patched Human Review fork, and `cloudflared`, and it verifies the exact public session before returning it. Confirm a submitted feedback batch reaches `human-review poll` before claiming external review works.
5. Use `subspace_review_gate_render_slack` and post the result as the Slack companion UI. Preserve route order and the reply-by-number instruction. Include the Human Review URL without wrapping punctuation or formatting it so Slack absorbs trailing characters.
6. Treat Human Review comments as annotations/evidence. Treat Slack replies as candidate resolutions. Use `subspace_review_gate_build_resolution` to validate a specific route; `revise` and `hold` require a rationale.
7. Only a workflow controller or dispatched leg may apply a binding Resolution to a Spacedock workflow. For an artifact without a workflow, save the portable Resolution alongside the Briefing and report the outcome; do not invent a workflow transition.

## Slack UI

- Always state the Briefing ID, question, fixed revision, ordered choices, and `Reply with the option number`.
- Use a plain link for Human Review. Do not include trailing `*`, `)`, or punctuation in the hyperlink destination.
- Use native Slack option controls only for an explicit decision opportunity. Their selected value must map to exactly one route ID; free-form discussion remains advisory.
- `[Q]` means answer/discuss only. `[RES]` requires an explicit entity-specific choice or imperative. Default to `[Q]`.

## Safety

- A Briefing is immutable. New artifact bytes, question, or routes require a new ID.
- Do not treat `approve` as sufficient routing information: preserve the selected route ID and destination.
- Do not expose a Human Review server through an unauthenticated public URL for sensitive artifacts. Prefer Tailnet during development; use an authenticated named tunnel for durable access.
- Never let Slack or Human Review directly write a Spacedock verdict.

## Verification

A review is complete only when all are true:

- Briefing verification passes.
- Human Review can submit a feedback batch to the waiting poll.
- Slack shows the same ordered routes as the Briefing.
- Any resolution validates to one route and includes rationale when required.
- A workflow mutation, if any, is reported separately with controller evidence.
