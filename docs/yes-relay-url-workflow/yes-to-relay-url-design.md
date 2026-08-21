---
id: pj0cksg00ebxtyvbaabv2kdz
title: Yes to Relay URL design
status: validation
source: Captain commission resolution
started: 2026-08-21T07:42:39Z
completed:
verdict:
score: 1.0
worktree: .worktrees/spacedock-ensign-yes-to-relay-url-design
issue:
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:pj0cksg00ebxtyvbaabv2kdz:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:pj0cksg00ebxtyvbaabv2kdz-ideation-1
              briefing:
                id: briefing:pj0cksg00ebxtyvbaabv2kdz:ideation:attempt-1:revision-1
                digest: sha256:1c5ab49eadf262614e5953f7fbbe8a8b76cd26d00d604707145269d1200e771b
                request-digest: sha256:5d9b27c3c55c75cc239cec96cfe056fd7b5a20b6cebfa1d9cbd89684538d3df5
                room-ref: ./yes-to-relay-url-design/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:pj0cksg00ebxtyvbaabv2kdz:ideation:1
                briefing: briefing:pj0cksg00ebxtyvbaabv2kdz:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-21T08:49:57.414622Z"
                decision: approve
                reason: 接受設計；implementation 必須採用 Room-scoped 背景等待 feedback，不阻塞 Slack foreground；按 Result ID 去重，owner pull 並驗證 exact bytes，回原 thread 通知；Room disabled、Briefing expired、使用者停止或設定的一位 reviewer 首份有效 feedback 時停止，並具備 process restart 後 cursor recovery。
              application:
                target-stage: implementation
                state: consumed
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

## Stage Report: ideation

### Summary

The design fixes one narrow journey: a disclosed offer for one finished, identifiable artifact, a clear Yes, fail-closed repository-derived preflight, immutable packaging/publication, then only a validated safe Room URL and actual `expiresAt`. This stage produced review artifacts only; it made no implementation or runtime change.

### Checklist

- [x] DONE — Design artifacts are complete and exact-byte identified below.
- [x] DONE — The 1440×1800 browser render has no measured overflow, clipping, overlap, or arrow-gap failure.
- [x] DONE — Repository capability, limit, lifecycle, ownership, and AC-1–AC-5 evidence is recorded below.

### Bound artifacts

- `design-prototypes/architecture-ux.html` — SHA-256 `0aa47f225ac002e14553621a76d4629b3f94f2af7007d820b07cbd1759d8c808`
- `design-prototypes/architecture-ux.png` — SHA-256 `a9ef27f1ce9d4cfa461f7d244cab2d5ba07e4aec5d44206eefab7ddea3ba0e89`; PNG `1440x1800`
- `design-prototypes/product-rules-acceptance.md` — SHA-256 `0ca54aadf7ecb671c5182ae4e637ad08154de24c7fa9dd7fe9b77ab471b9834d`

### Render evidence

Playwright measured viewport `1440x1800`; document `scrollWidth/clientWidth 1440/1440` and `scrollHeight/clientHeight 1800/1800`; body `1440/1440`; 17 boxes; `childOverflowCount 0`; `overlapCount 0`; `arrowGapFailureCount 0`; `.step` overflow mode `visible`. The Playwright screenshot and independent PNG inspection both report `1440x1800`.

### Repository and source evidence

- Actual Hermes limits and behavior: `bin/subspace-review-relay:16,40-55,59-107` enforces a safe relative URI with 1–8 simple segments, exactly one artifact, SHA-256/size checks, and byte-identical packaging; `bin/subspace-review-relay:110-166,240-268` keeps owner state private, returns only private `room_ref` from Room creation, and validates disable/revoke timestamps. No repository source documents an upload-size cap or accepted-media allowlist, so those remain unknown and preflight blocks rather than inventing values.
- Ownership/capability boundary: `README.md:33-52` says the plugin is the owner client, Relay owns the Room/browser session, the Room URL is a bearer capability, session IDs are not discoverable, and `bin/subspace-relay-web` is only a legacy local development viewer.
- Relay source at `spacedock-dev/subspace-relay@48f4b7ed7ac0a4395350fd24e5a90a9a8e2dfc5d`: `netlify/lib/briefing.ts:70-77,99-115,124-159,532-539` defines the configurable 30-day default, stamps `expiresAt`, and refuses capability access after expiry; `netlify/lib/retention-sweeper.ts:88-97,391-398,507-522` separately establishes sweep eligibility and later byte reclamation. Therefore actual returned `expiresAt` is authoritative; expiry is not exact-second physical deletion.

### Acceptance evidence

- **AC-1:** The HTML journey and product rules limit the trigger to one finished identifiable artifact and reject silence, emoji, vague assent, and changed consent facts; only clear Yes authorizes upload/publication.
- **AC-2:** The cited Hermes and Relay source defines known limits and behavior; `product-rules-acceptance.md` rejects missing, unreadable, sensitive, unsupported, changed, and unknown-limit inputs and returns no URL on incomplete or untrusted responses.
- **AC-3:** The self-contained HTML rendered to the bound `1440x1800` PNG with the zero-failure browser measurements above.
- **AC-4:** Both artifacts distinguish Room disable, Briefing revoke/expiry, session revoke, sweeper reclamation, and future hard deletion, including confirmation and recoverability language; none is mislabeled as deletion.
- **AC-5:** The three artifacts have exact local SHA-256 revisions above, making mutation detectable when a later local human gate binds the artifacts and this stage report. No gate was published in this stage.

### Ownership, deferral, and exclusions

`spacedock-dev/subspace-hermes` owns only the Hermes plugin/owner-client integration; the hosted browser/Web UI belongs in `spacedock-dev/subspace-relay`, and Hermes must not grow a divergent viewer. Inventory and cleanup of legacy Hermes Web surfaces (`web/`, `bin/subspace-relay-web`, related tests/docs, and prototypes) is deferred to a bounded implementation stage; this design stage deletes nothing.

Explicitly excluded: implementation, publication, push, PR, merge, release, deployment, Relay upload/Room creation, hard deletion, and any live runtime or remote-system modification.

## Stage Report: implementation
- DONE: One explicit-consent operation now performs fail-closed capability preflight, immutable Briefing create/verify/package/publish, and Room creation, returning only validated `room_url` and authoritative normalized `expires_at`; identical successful replay uses `0600` private operation state and makes zero additional network calls.
  Evidence for AC-1, AC-2, and AC-5: the focused consent-operation test passed (1 test), observed only the capability, Briefing, and Room requests on first invocation, and observed no additional requests on identical replay.
- DONE: The Room-scoped watcher runs in the background, persists Result-ID cursor state, owner-pulls and exact-byte verifies feedback-only Results against Room/Briefing/artifact/digests, emits only one safe advisory event to the dispatch-bound Slack origin, never advances workflow state, and supports Room-disabled, Briefing-expired, explicit-stop, and first-valid-feedback termination.
  Evidence for AC-4 and AC-5: `python3 -m unittest tests.test_relay_consent -v` passed all 5 tests, and full test discovery passed all 50 tests.
- DONE: Removed the legacy `web/` viewer, `bin/subspace-relay-web`, and related tests/prototype while preserving Hermes plugin/owner-client tools and documentation; focused and full verification pass without network publication or runtime side effects.
  Evidence for AC-3: full test discovery passed all 50 tests, and the reported `py_compile` check passed for `__init__.py`, `bin/subspace-review-gate`, `bin/subspace-review-relay`, and `bin/subspace-review-runtime`.

### Summary

Implemented the consent-gated Relay owner-client flow and Room-scoped background feedback watcher, removed the duplicated legacy Hermes Web viewer, and fixed successful consent-operation replay so an identical fixed operation returns its private cached safe payload without repeating preflight, publication, or Room creation. The idempotency key is derived from the resolved artifact, exact revision, question, audience, media type, sensitivity, normalized endpoint, and private output locations; changed facts therefore cannot borrow an earlier success. No live Relay publication, runtime change, push, PR, merge, release, or deploy occurred.

### Verification evidence

- `python3 -m unittest tests.test_relay_consent.RelayConsentOperationTests.test_clear_yes_runs_preflight_and_returns_only_safe_room_url_and_expiry` — PASS (1 test); the first invocation observed only `GET /api/capabilities/review-room`, `POST /api/briefing`, and `POST /api/room`, while identical replay returned the same safe payload with no additional requests.
- `python3 -m unittest tests.test_relay_consent -v` — PASS (5 tests).
- `python3 -m unittest discover -s tests -v` — PASS (50 tests).
- `python3 -m py_compile __init__.py bin/subspace-review-gate bin/subspace-review-relay bin/subspace-review-runtime` — PASS.
- `git diff --check` — PASS.
