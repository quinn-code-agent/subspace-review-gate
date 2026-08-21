---
id: pj0cksg00ebxtyvbaabv2kdz
title: Yes to Relay URL design
status: ideation
source: Captain commission resolution
started:
completed:
verdict:
score: 1.0
worktree:
issue:
pr:
mod-block:
---

Create and verify a reviewable architecture and UX design for a future high-level operation that turns a clear Yes into a safe Relay Room URL for one finished identifiable artifact. Stop at the design artifact confirmation gate; do not implement or deliver the feature.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: Limited real use in Hermes Slack channels would create persistent Relay review value and likely iteration, while this commission changes no runtime, publishes nothing, and accepts no production operations.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Define one explicit-review-request journey from offer through safe URL and expiry.
      - Derive actual Relay limits and fail-closed boundaries from the repository.
      - Separate Room disable, Briefing revoke or expiry, and future hard deletion.
    implementation:
      - Future only; preserve explicit-Yes authorization and never expose owner or session secrets in Slack.
      - Future only; use create, verify, package, publish, Room sequencing with immutable revision semantics.
    testing:
      - Verify the self-contained HTML render and exact PNG dimensions without overflow, clipping, or overlaps.
      - Cite repository evidence for actual limits and acceptance-rule coverage.
  scope_boundary: This run produces design artifacts only and excludes implementation, push, PR, merge, release, deploy, Relay publish, and live runtime modification.
  promote_when:
    - Broad exposure, production data or credentials, unattended operation, SLO or support duty, irreversible migration, or release and rollback ownership enters accepted scope.
  decision:
    authority: Captain Kent
    at: 2026-08-21T00:00:00+08:00
```

## Accepted journey

An explicit request to review a finished identifiable artifact triggers a disclosed Relay offer in the same Hermes-managed Slack channel. Repository-derived preflight must pass. Only a clear Yes authorizes upload and Room publication; the response returns a safe bearer-capability URL and actual `expiresAt` without owner/session secrets.

## Acceptance criteria

**AC-1 — The design defines the trigger narrowly and preserves explicit authorization.**
Verified by: the rendered flow contains negative non-trigger cases and a distinct clear-Yes branch; changing the Yes branch to accept silence, emoji, or vague assent makes visual and rules review fail.

**AC-2 — Preflight and disclosures are fail-closed and repository-derived.**
Verified by: the stage report cites concrete repository paths for capability/limit claims and the product rules reject sensitive, unsupported, unreadable, changed, or unknown-limit artifacts; removing a cited limit or a rejection class makes the evidence incomplete.

**AC-3 — The review package is readable and mechanically renderable.**
Verified by: a self-contained HTML file renders to a PNG with reported dimensions and checks showing zero horizontal overflow, no clipping, and no overlapping labels or arrows; any positive overflow or overlap count fails.

**AC-4 — Lifecycle language cannot misrepresent deletion.**
Verified by: the design and rules separately name Room disable, Briefing revoke/expiry, and future hard deletion with scope, recoverability, and immediate-versus-queued confirmation requirements; labeling disable/revoke as delete fails.

**AC-5 — The artifacts are exact-byte reviewable at a local human gate.**
Verified by: Spacedock gate preparation emits a durable digest/open Room bound to the HTML, PNG, rules Markdown, and stage report; mutation of any bound artifact causes gate validation or replay to reject as stale.

## Out of scope

Feature implementation; remote writes; push, PR, merge, release, deploy; Relay publication; live runtime modification; owner/session secret disclosure; and destructive hard deletion.
