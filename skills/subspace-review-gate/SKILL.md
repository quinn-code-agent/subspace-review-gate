---
name: subspace-review-gate
description: Review fixed artifacts and hand off decisions safely.
version: 0.2.0
author: Kent, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [review, decision, handoff, subspace, relay, slack]
    related_skills: []
---

# Subspace Review & Gate

Use this skill to move a fixed artifact through review without losing which version was read, what feedback was given, or which option was selected. It uses the portable Subspace Review & Gate v1 contract. It does not give a reviewer, Relay, Slack, or this plugin authority to write a workflow verdict.

## When to Use

Use this skill when:

- a README, document, design preview, proposal, specification, or implementation plan is ready for review;
- a discussion has become a short fixed decision note that people or agents can read;
- several people or agents need asynchronous feedback on the same revision;
- a decision needs explicit routes, rationale, and a durable handoff between Hermes, Slack, a browser reviewer, or Relay;
- the next collaborator must know exactly which artifact bytes were reviewed.

Do not use this skill for ordinary open-ended conversation. Answer or discuss normally when there is no fixed artifact or decision opportunity. If durable review or handoff becomes necessary, first write the short proposal, decision note, design, or plan that people can actually review.

## Prerequisites

- Confirm the `subspace_review_gate` toolset is available before creating a Briefing.
- Finish and render or otherwise verify the artifact before opening review.
- Use a temporary public Human Review surface only for non-sensitive artifacts and only after its runtime prerequisites are available.
- Use Relay Room owner operations only with the profile-local private owner receipt. A Room URL is a capability and is never automatically posted or delivered.

## Procedure

1. **Fix the review unit.** Create one complete artifact with one review question. Completion criterion: the artifact path, media type, question, and intended reviewer are known.
2. **Create and verify the Briefing.** Use `subspace_review_gate_create`, then `subspace_review_gate_verify`. Completion criterion: the artifact bytes match the Briefing's SHA-256 revision. New bytes, question, or routes require a new Briefing.
3. **Choose the review surface.**
   - For a normal fixed-artifact review, use the appropriate local or Human Review surface and `subspace_review_gate_render_slack`.
   - For a Relay-hosted browser review, use the owner-client tools to publish, create a Room, list results, and pull a Result. Do not host the browser yourself or expose the Room capability automatically.
   Completion criterion: every reviewer sees the same fixed Briefing revision.
4. **Collect feedback as evidence.** Treat reviewer comments as portable `Annotation` evidence. Treat a Relay feedback Result as feedback only. Completion criterion: evidence is tied to the Briefing and does not alter artifact bytes.
5. **Handle discussion and decisions separately.** `[Q]` means answer or discuss only. `[RES]` requires an explicit entity-specific choice or imperative. For an explicit route selection, use `subspace_review_gate_build_resolution`; `revise` and `hold` require a reason or included Annotation. Completion criterion: the chosen route ID and destination are unambiguous.
6. **Hand off workflow changes.** Only a workflow controller or dispatched leg may apply a binding Resolution to a workflow. For an artifact without a workflow, preserve the portable outcome beside the Briefing. Completion criterion: any state change has separate controller evidence.

## Slack projection

- Render Slack from the same Briefing, not from a paraphrase.
- Include Briefing ID, question, fixed revision, ordered routes, and `Reply with the option number`.
- A free-form reply, question, comment, or emoji is advisory. A native Slack option control is valid only when it maps to one exact route ID.
- Preserve the exact route ID and destination. `approve` by itself is not enough routing information.

## Pitfalls

- Do not open a review on unfinished or unverified bytes.
- Do not treat a Room URL, share URL, owner receipt, device secret, session value, or Result envelope as ordinary message content.
- Do not turn a self-declared reviewer name into verified identity or workflow authority.
- Do not let Slack, Human Review, Relay, or a browser viewer directly write a workflow verdict.
- Do not claim a public review works because a page returned HTTP 200; require actual submitted feedback evidence.

## Verification

A review or handoff is complete only when all applicable checks pass:

- Briefing verification succeeds against the reviewed artifact bytes.
- The reviewer surface received or submitted feedback as intended.
- Slack shows the same routes and ordering as the Briefing.
- A Resolution, if present, maps to exactly one route and has required rationale.
- Relay owner operations retain capability material in profile-local private state.
- A workflow mutation, if any, is separately reported with workflow-controller evidence.
