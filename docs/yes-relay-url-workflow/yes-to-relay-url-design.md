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

## Stage Report: validation
- FAILED: The clear-Yes path passes the focused synthetic journey and identical completed replay makes zero additional network calls, but the exact candidate accepts an already-expired `expiresAt` as a successful safe payload and accepts owner-secret receipts with mode `0644`; therefore safe expiry and private-state fail-closed requirements are not met.
  Evidence for AC-1 and AC-2: focused tests passed, while the adversarial probe printed `PROBE past_expires_at: ACCEPTED 2020-01-01T00:00:00Z` and `PROBE owner_receipt_mode_0644: ACCEPTED`; `bin/subspace-review-relay:223-230,605-667` performs syntax-only expiry normalization with no future-time check, and `bin/subspace-review-relay:179-190` reads owner credentials without permission validation.
- FAILED: The background watcher does not preserve immutable Result-ID or Slack origin-thread binding across restart/re-entry, and its detached-process launcher neither records/reuses a process nor verifies startup; these are blocking defects in the accepted Room-scoped background design.
  Evidence for AC-4 and AC-5: the adversarial local Relay seam listed Result `res_bbbbbbbbbbbbbbbbbbbbbbbbbb` but served exact bytes whose embedded id was `res_cccccccccccccccccccccccccccc`; the candidate accepted them and emitted `event_id=relay-feedback:res_bbbbbbbbbbbbbbbbbbbbbbbbbb`. A persisted cursor bound to `C_ORIGINAL/1.1` was then accepted with caller-supplied `C_OTHER/9.9`. `bin/subspace-review-relay:678-694` never checks the pulled Result id against the listed id, `:718-759` stores but never enforces cursor origin, and `__init__.py:157-178` unconditionally spawns and returns a PID without durable process identity, readiness, reuse, or shutdown verification. Raw feedback remained absent from the emitted event and no workflow mutation exists, but those positives do not repair the binding failures.
- DONE: Repository boundary and compatibility checks pass: the duplicated Hermes Web viewer is removed while plugin/owner-client registration, manifests, docs, focused/full tests, compilation, and diff hygiene remain green.
  Evidence for AC-3: exact candidate `07fcf30fb5acc8effd5f11cf41480cab0b2fe53d`; `python3 -m unittest tests.test_relay_consent -v` passed 5/5, `python3 -m unittest discover -s tests -v` passed 50/50, `python3 -m py_compile __init__.py bin/subspace-review-gate bin/subspace-review-relay bin/subspace-review-runtime` passed, and both `git diff --check 4ee685f9dd52a782e03710c6413008b1aa6ca3ec..HEAD` and clean-worktree diff checks passed. The full 18-file implementation diff from `4ee685f9dd52a782e03710c6413008b1aa6ca3ec` through candidate HEAD was inspected; removals are limited to the duplicate Web viewer/prototype/tests and owner-client tools remain registered.

### Summary

REJECT. Candidate `07fcf30fb5acc8effd5f11cf41480cab0b2fe53d` is test-green and preserves the owner-client repository boundary, but fresh adversarial validation found blocking expiry/private-state and watcher identity/origin/process-lifecycle defects. No implementation code was changed; this validation committed only the report.

### Commands and results

- `python3 -m unittest tests.test_relay_consent -v` — PASS, 5 tests.
- `python3 -m unittest discover -s tests -v` — PASS, 50 tests.
- `python3 -m py_compile __init__.py bin/subspace-review-gate bin/subspace-review-relay bin/subspace-review-runtime` — PASS.
- `git diff --check 4ee685f9dd52a782e03710c6413008b1aa6ca3ec..HEAD` — PASS.
- `git diff --check && git diff --exit-code HEAD -- .` — PASS before the report edit; worktree was clean at candidate HEAD.
- `git diff --stat --name-status 4ee685f9dd52a782e03710c6413008b1aa6ca3ec..HEAD` plus full per-file diff inspection — 18 files, 656 insertions, 270 deletions; all implementation and removal surfaces inspected.
- Ephemeral local adversarial probe (removed after execution) — reproduced acceptance of mode-`0644` owner state, past expiry, mismatched embedded/listed Result identity, and changed origin against a persisted cursor. It used only local/synthetic HTTP seams and made no real Relay publication.

### Findings and residuals

1. Blocking: require authoritative expiry to be valid and future before returning/caching a Room URL; replay must re-evaluate expiry safely.
2. Blocking: validate private owner/cursor/Room/operation state permissions on read and use atomic private writes; current chmod-after-write is not a complete private-state guarantee.
3. Blocking: bind pulled Result identity to the listed Result ID in addition to Room, Briefing, artifact, mode, and digests.
4. Blocking: freeze and enforce origin channel/thread and outbox for one Room watcher across cursor recovery; caller-supplied rebinding must refuse.
5. Blocking: make watcher lifecycle durable and idempotent—readiness-checked start, one live watcher per bound identity, restart/reuse semantics, and verified stop/shutdown. The current outbox-before-cursor ordering also leaves a crash window for duplicate delivery; downstream event-id dedupe is not demonstrated here.
6. Residual: credential-bearing `urllib` calls still use the default redirect-following opener; exact HTTPS-origin pinning/redirect refusal was not demonstrated by this candidate and should be covered before real Relay use.

### Recommendation

REJECT and return to implementation. Re-run the same focused/full/compile/diff gates plus red-capable adversarial tests for every blocking finding against the new exact candidate SHA. No push, PR, merge, release, deploy, runtime apply, or real Relay publication occurred.

## Stage Report: implementation (cycle 2)
- DONE: Fixed authoritative Room expiry handling and private state I/O: expired Room capabilities now refuse before caching, credential-bearing owner/Room/cursor/operation files require private regular-file state, and writes are atomic `0600` replacements.
  Evidence for AC-1 and AC-2: `tests.test_relay_consent` passed all 11 tests, including expired authoritative expiry and mode-`0644` owner-state refusal; legacy compatibility fixtures now explicitly create only credential-bearing owner/Room records as `0600` without weakening production validation.
- DONE: Fixed credentialed transport and immutable feedback identity/binding: credential-bearing redirects and origin changes refuse, listed and embedded Result IDs must match, persisted Slack origin/outbox bindings cannot be rebound, and crash-window replay deduplicates the durable event ID.
  Evidence for AC-2 and AC-4: the redirect, Result-identity, cursor-rebinding, Room-scope, and outbox replay adversarial tests all passed in the 11-test consent suite.
- DONE: Completed the watcher readiness contract: `watch-feedback` accepts `--ready-file`, validates private owner/Room/cursor and immutable binding state before polling, atomically writes a `0600` marker carrying PID plus nonce-bound identity, and the plugin waits for and validates that marker before returning `pid` and `ready`.
  Evidence for AC-4 and AC-5: the focused lifecycle test passed 1/1; an identical start reused the same proven live PID, while a changed origin binding refused.
- DONE: Completed durable safe stop: the plugin persists the explicit user-stop marker, loads and validates the private durable process record, proves the full CLI binding and nonce before any signal, waits for actual process exit, removes live-process/readiness state only after shutdown, and reports `shutdown_verified` only from verified exit rather than marker existence.
  Evidence for AC-4 and AC-5: the focused lifecycle test passed 1/1, asserted `shutdown_verified`, and independently observed `ProcessLookupError` for the stopped PID; the durable `.stop` marker leaves subsequent watcher state as `user-stop`.
- DONE: Preserved the Hermes owner-client repository boundary and compatibility while completing cycle 2 locally.
  Evidence for AC-3 and AC-5: `tests.test_relay` passed 14/14, full discovery passed 56/56, compilation and diff hygiene passed, and no removed Web viewer or runtime/publication surface was restored.

### Summary

Cycle 2 closes the five validation findings: future authoritative expiry, atomic/private secret state, exact Result identity, immutable watcher origin/outbox binding with durable dedupe, and readiness/idempotent-start/verified-stop lifecycle. No push, PR, merge, release, deploy, runtime apply, or real Relay publication occurred.

### Commands and results

- `python3 -m unittest tests.test_relay_consent.RelayFeedbackWatcherTests.test_background_watcher_start_is_ready_idempotent_and_stop_is_verified -v` — PASS, 1 test.
- `python3 -m unittest tests.test_relay_consent -v` — PASS, 11 tests.
- `python3 -m unittest tests.test_relay -v` — PASS, 14 tests.
- `python3 -m unittest discover -s tests -v` — PASS, 56 tests.
- `python3 -m py_compile __init__.py bin/subspace-review-gate bin/subspace-review-relay bin/subspace-review-runtime tests/test_relay.py tests/test_relay_consent.py` — PASS.
- `git diff --check` — PASS.

### Findings fixed

1. Expired authoritative `expiresAt` values could be returned/cached; they now fail closed and replay revalidates future expiry.
2. Credential-bearing state could be read at mode `0644` and writes used chmod-after-write; reads now enforce private regular files and production writes use atomic mode-`0600` replacement.
3. Pulled feedback could borrow a listed Result ID while embedding another ID; exact listed/embedded identity is now required.
4. Persisted watcher origin/outbox state could be rebound and outbox-before-cursor replay could duplicate delivery; binding is immutable and event append is durably deduplicated.
5. Background start lacked readiness, durable process identity, reuse, and verified shutdown; readiness and process records now bind the full watcher arguments plus nonce, identical live starts reuse one PID, changed binding refuses, and stop is verified by process exit rather than marker alone.
6. Credentialed `urllib` calls could follow redirects or change origin; the exact credentialed origin is pinned and redirects refuse.

### Residuals

No blocking residual remains within cycle-2 watcher lifecycle or legacy fixture compatibility scope. Stop without a durable process record deliberately returns `shutdown_verified: false`; an unproven or PID-reused process is never signalled. Remote and runtime operations remain explicitly unperformed.

## Stage Report: validation (cycle 2)
- FAILED: Candidate `24df29f2f2240372976b15963957ec041454141b` still does not prove the full watcher command before signalling: `_pid_is_watcher` accepts an unrelated Python sleeper when the expected Relay path, subcommand, flags, values, and nonce are merely appended to its argv, and stop then sends SIGTERM to that unrelated PID.
  Evidence for AC-4 and AC-5: an independent local adversarial probe reported `unrelated_classified_as_watcher: true` and `unrelated_process_was_signalled: true`; the stop result still had `shutdown_verified: false`. This refutes the required full-command/PID-reuse refusal and makes safe watcher termination a blocking failure.
- DONE: The remaining cycle-2 consent, private-state, transport, immutable feedback, origin, and dedupe corrections reproduced successfully: expired authoritative expiry refuses without an operation cache; replay re-evaluates expiry; owner/Room/cursor/operation/readiness/process records use the common private-file checks; listed and embedded Result IDs must match; origin/thread/outbox cannot be rebound; durable event ID replay emits no duplicate; credential-bearing redirects and changed origins refuse; and readiness follows validated binding state.
  Evidence for AC-1, AC-2, AC-4, and AC-5: `tests.test_relay_consent` passed 11/11, including the focused clear-Yes, expired-expiry, redirect, Result-ID, rebinding, dedupe, readiness/reuse, and stop cases. The independent private-state probe refused mode `0644`, symlink, and directory inputs and observed atomic inode replacement to a regular `0600` file.
- DONE: Repository ownership and compatibility remain intact: the duplicate Hermes Web viewer surfaces stay removed, plugin/owner-client tools and docs remain present, and all required focused/full/compile/diff gates pass on the exact candidate.
  Evidence for AC-3 and AC-5: `tests.test_relay` passed 14/14, full discovery passed 56/56, `py_compile` passed, both correction-range and clean-worktree diff checks passed, and complete diff inspection from `ef3ef746` through candidate HEAD found only `__init__.py`, `bin/subspace-review-relay`, the entity receipt, and focused relay tests changed.

### Summary

REJECT. Exact candidate `24df29f2f2240372976b15963957ec041454141b` closes the expiry, private-state, immutable Result, origin/outbox, dedupe, redirect, readiness, and ordinary idempotent lifecycle findings, but the process-identity predicate is not a full-command proof and can signal an unrelated synthetic process whose argv contains the expected tokens. No implementation code was changed in validation; only this report was added.

### Commands and results

- `python3 -m unittest tests.test_relay_consent -v` — PASS, 11 tests.
- `python3 -m unittest tests.test_relay -v` — PASS, 14 tests.
- `python3 -m unittest discover -s tests -v` — PASS, 56 tests.
- `python3 -m py_compile __init__.py bin/subspace-review-gate bin/subspace-review-relay bin/subspace-review-runtime tests/test_relay.py tests/test_relay_consent.py` — PASS.
- `git diff --check ef3ef746..HEAD && git diff --check && git diff --exit-code HEAD -- .` — PASS before this report edit; candidate worktree was clean.
- `git diff --find-renames --find-copies --name-status ef3ef746..HEAD` plus complete per-file correction-diff inspection — 5 files, 604 insertions, 64 deletions; production changes are confined to plugin watcher lifecycle and Relay adapter hardening, with tests and state receipt updates.
- Ownership cleanup check for absent `web/`, `bin/subspace-relay-web`, `tests/test_web.py`, and `design-prototypes/relay-web-prototype.html`, plus full `4ee685f9..HEAD` name-status review — PASS; owner-client tools, manifest, README, setup, architecture, and skill surfaces remain.
- Ephemeral independent local probe (removed after execution) — atomic private replacement produced a regular mode-`0600` file with a changed inode; mode-`0644`, symlink, and directory private-state reads refused; forged extra-payload argv was misclassified as the watcher and the unrelated synthetic sleeper received SIGTERM.

### Finding and residuals

1. Blocking: `_pid_is_watcher` checks token membership and first flag values but does not compare an exact expected argv or executable identity. A different Python program can carry the expected Relay tokens as inert extra arguments, pass classification, and be signalled by `relay_stop_feedback_watch`. Build one canonical expected argv/fingerprint, require exact executable and argument-vector equality (with the persisted nonce), and add a red test proving extra prefix/payload/suffix argv and PID reuse never receive a signal.
2. Positive residual: stop correctly withholds `shutdown_verified` when exit is not proven, but that post-signal result does not undo an unsafe signal already sent.
3. Scope residual: no real Relay publication, push, PR, merge, release, deploy, or runtime apply was performed; the adversarial signal targeted only a validator-owned synthetic sleeper.

### Recommendation

REJECT and return to implementation for exact executable/full-argv process proof before any signal. Re-run the focused 11-test consent suite, 14-test relay suite, 56-test full suite, compile/diff gates, and an independent extra-argv/PID-reuse no-signal probe against the next exact candidate SHA.

## Stage Report: implementation (cycle 3)
- DONE: Replaced token-membership watcher classification with one canonical executable/full-argv identity constructed before spawn, SHA-256 fingerprinted, persisted in the private process record, and compared exactly against kernel-reported executable and argument boundaries before reuse, cleanup, or signalling.
  Evidence for AC-4 and AC-5: exact candidate `344539e0c569702ccc8af548a80644d8f57960b9`; the focused lifecycle test verifies the persisted executable, complete argv, and recomputed fingerprint, then proves ordinary identical reuse and verified shutdown.
- DONE: Added deterministic RED→GREEN coverage for the reproduced forged-extra-argv/PID-reuse attack; an unrelated Python sleeper with the complete expected watcher command appended as inert payload is refused on restart and stop, remains alive through both checks, and receives no signal.
  Evidence for AC-4 and AC-5: before the production fix, `test_forged_extra_argv_and_reused_pid_are_never_signalled` errored because unsafe signalling produced no `no signal was sent` refusal; after the fix, the focused lifecycle plus adversarial command passed 2/2 and the consent suite passed 12/12.
- DONE: Preserved all cycle-2 expiry, private-state, transport, Result-ID, origin/outbox, dedupe, readiness, idempotent reuse, and owner-client repository-boundary corrections with the required layered suites green.
  Evidence for AC-1, AC-2, AC-3, AC-4, and AC-5: `tests.test_relay_consent` passed 12/12, `tests.test_relay` passed 14/14, full discovery passed 57/57, and `py_compile` passed for all required plugin, Relay, runtime, and focused-test files.
- DONE: Kept the implementation leg local and side-effect free.
  Evidence for AC-2 and AC-5: correction-range and clean-worktree diff checks passed; no push, PR, merge, release, deploy, runtime apply, or real Relay publication was performed.

### Summary

Cycle 3 closes the remaining unsafe-signal finding by persisting and proving exact kernel executable plus full argv equality instead of searching command tokens. Any prefix, payload, suffix, duplicate/reordered flag, changed interpreter/script, fingerprint mismatch, or reused PID changes the exact identity, so reuse and stop fail closed without signalling. All prior cycle-2 protections remain green.

### Commands and results

- `python3 -m unittest tests.test_relay_consent.RelayFeedbackWatcherTests.test_background_watcher_start_is_ready_idempotent_and_stop_is_verified tests.test_relay_consent.RelayFeedbackWatcherTests.test_forged_extra_argv_and_reused_pid_are_never_signalled -v` — PASS, 2 tests.
- `python3 -m unittest tests.test_relay_consent -v` — PASS, 12 tests.
- `python3 -m unittest tests.test_relay -v` — PASS, 14 tests.
- `python3 -m unittest discover -s tests -v` — PASS, 57 tests.
- `python3 -m py_compile __init__.py bin/subspace-review-gate bin/subspace-review-relay bin/subspace-review-runtime tests/test_relay.py tests/test_relay_consent.py` — PASS.
- `git diff --check 24df29f2f2240372976b15963957ec041454141b..HEAD && git diff --check && git diff --exit-code HEAD -- .` — PASS before this report edit; candidate worktree was clean.

### Files changed

- `__init__.py` — canonical watcher command construction, Darwin/Linux kernel process identity reads, durable identity fingerprinting, exact comparison, and fail-closed live-PID restart handling.
- `tests/test_relay_consent.py` — persisted-identity assertions and the real forged-extra-argv/PID-reuse no-signal regression.
- `docs/yes-relay-url-workflow/yes-to-relay-url-design.md` — this cycle-3 implementation receipt.

### Residuals

No blocking residual remains in the assigned exact-process-identity correction. Unsupported operating systems fail closed because no exact kernel argv boundary reader is available. No remote or runtime operation was performed.
