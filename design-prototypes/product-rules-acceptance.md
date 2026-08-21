# Yes to Relay URL — product rules

Design only. This specifies one future Hermes operation; it does not publish, mutate Relay, or promise unsupported service behavior.

## Trigger and authorization

1. Trigger only when a person asks to review one finished, identifiable artifact in a Hermes-managed Slack channel. Draft discussion, “take a look sometime,” a bare file drop, multiple artifacts, emoji, silence, and vague assent do not trigger the operation.
2. Before asking for consent, name the artifact, its local revision, the review question, intended Relay audience, and expiry that an actual Relay capability response, preflight, or receipt confirms. Relay's production default is 30 days only when that actual response confirms it; never substitute a locally assumed default. State that the URL is a bearer capability: anyone holding it may reach the Room.
3. Only an unambiguous affirmative reply to that specific offer—such as “Yes” or “Yes, share it”—authorizes upload and Room publication. Consent is single-use and invalid if the artifact, question, channel, audience, expiry, or preflight facts change. Ask again after change.

## Fail-closed preflight

Reject before offering when the artifact is missing, unreadable, not a regular file, sensitive, unsupported, unfinished/unidentifiable, or not exactly one artifact; when its relative URI is unsafe or has more than eight simple segments; when its SHA-256 revision cannot be fixed and reverified; when the Relay endpoint or private owner-state location is unavailable; or when the actual Relay capability/preflight/receipt does not confirm the artifact's acceptance, effective expiry, and URL-return contract. An undocumented upload cap or accepted-media allowlist is an unknown, not a limit to invent.

The current Hermes repository proves one-artifact packaging, relative URI validation, digest/byte verification, and private owner state. It does **not** document an artifact upload-size cap or accepted-media allowlist, and current `create-room` returns only a private `room_ref`, not a safe URL or `expiresAt`. Upstream Relay code has a configurable production default of 30 days, but a future Hermes implementation must obtain and validate the effective expiry from an actual Relay capability/preflight/receipt; it must not infer that the default is active.

## Authorized sequence and output

After the clear Yes, run exactly: create immutable Briefing → verify current artifact bytes → package one artifact → publish package → create Room → validate returned safe Room URL and RFC 3339 `expiresAt` → post only that URL and expiry to the same channel. Reverify immediately before packaging/publish and abort if bytes changed. Retry may reuse operation-specific idempotency state only for the identical fixed revision; a changed revision requires a new Briefing and consent.

Never put device IDs/secrets, owner receipts, `room_ref`, Room IDs, session IDs, reviewer receipts, Result envelopes, filesystem paths, or remote error bodies in Slack. If any step fails or the response is incomplete/untrusted, return no URL, disclose that nothing shareable was produced, and preserve private recovery state for an authorized operator.

## Repository ownership and future implementation boundary

`spacedock-dev/subspace-hermes` owns only the Hermes owner-client/plugin integration: plugin tools, private owner state, fixed-artifact packaging, and the Slack offer plus clear-Yes consent. `spacedock-dev/subspace-relay` owns Relay Rooms, the browser/hosted reviewer UI, sessions, capability URLs, storage, access expiry, and retention sweeping. Hermes must not carry a duplicated or divergent viewer.

A bounded future implementation must inventory the current legacy Web surfaces—`web/`, `bin/subspace-relay-web`, related tests/docs, and design prototypes—and remove duplicated hosted/local Web implementation and stale instructions. An item may remain only when a concrete plugin-runtime necessity is documented and it does not form a divergent viewer. This design-only stage deletes none of those files.

## Lifecycle language

| Action | Scope and effect | Confirmation rule |
| --- | --- | --- |
| Room disable | Stops Room access for all sessions; retained Briefing/package/Results are not claimed deleted. | Confirm only from Relay `disabledAt`; say “Room disabled,” never “deleted.” |
| Briefing revoke or expiry | Ends capability access under Relay policy; not implemented here and not equivalent to Room disable. | Actual Relay `expiresAt` is authoritative. The production default is 30 days only when an actual capability/preflight/receipt confirms it. |
| Session revoke | Ends one already-known reviewer session; siblings remain. IDs are not discoverable here. | Confirm only from Relay `revokedAt`; never request, guess, derive, or expose the ID in Slack. |
| Sweeper byte reclamation / future hard deletion | Expiry stops access; the retention sweeper later reclaims stored bytes. A separate future hard-delete operation is not claimed. | Never present expiry as exact-second physical deletion. If deletion is queued, say “deletion requested,” not “deleted.” |

Expiry is Relay's actual `expiresAt`, not a locally calculated promise. At that timestamp access stops; a later sweeper reclaims bytes, so expiry does not prove exact-second physical deletion.

## Acceptance checks

- Replacing clear Yes with silence, emoji, or vague assent must prevent upload and Room creation.
- Changing artifact bytes after consent must fail revision verification and produce no URL.
- Removing any required capability/limit fact must make preflight fail closed.
- Injecting owner/session material or a remote error body must prove it cannot enter Slack output.
- A malformed URL, absent/malformed `expiresAt`, or mismatched Briefing identity must produce no URL.
- Lifecycle copy fails if disable/revoke is called delete, expiry is equated with byte deletion, or queued deletion is reported complete.
- Repository-boundary review fails unless legacy Hermes Web surfaces are inventoried and every duplicated viewer/stale instruction is removed or retained only with concrete plugin-runtime necessity; no divergent viewer is allowed.

## Repository evidence

- `bin/subspace-review-relay:14-43,48-56` — safe relative URI (1–8 segments), valid Briefing identity, exactly one artifact.
- `bin/subspace-review-relay:59-107` — artifact/Briefing digest verification and package byte integrity.
- `bin/subspace-review-relay:110-166` — private 0600 owner receipt; credentials withheld from publish output.
- `bin/subspace-review-relay:240-268` — create returns private `room_ref`; disable and session revoke validate timestamps.
- `README.md:33-52` and `docs/setup-for-hermes-agents.md:122-148` — URL-as-capability, deliberate delivery, private controls, ID non-discoverability, authority boundaries.
- `README.md:46-52` — Hermes is the owner client; Relay owns the Room/browser session; `bin/subspace-relay-web` is a legacy local development viewer rather than a Room host.
- `tests/test_relay.py` — secret non-echo, frozen owner routes, timestamp validation, remote error-body suppression.
- `spacedock-dev/subspace-relay@48f4b7ed7ac0a4395350fd24e5a90a9a8e2dfc5d:netlify/lib/briefing.ts:70-77,99-115,124-159,532-539` — configurable 30-day default, stamped `expiresAt`, and access refusal after expiry.
- `spacedock-dev/subspace-relay@48f4b7ed7ac0a4395350fd24e5a90a9a8e2dfc5d:netlify/lib/retention-sweeper.ts:88-97,391-398,507-522` — later sweep eligibility and byte reclamation are separate from access expiry.
