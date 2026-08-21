---
commissioned-by: spacedock@0.27.0-pre8
entity-type: pilot_work_item
entity-label: work item
entity-label-plural: work items
id-style: sd-b32
state: $inline
stages:
  defaults: {worktree: false, concurrency: 1}
  states:
    - {name: backlog, initial: true}
    - {name: ideation, worktree: true, gate: true}
    - {name: implementation, worktree: true}
    - {name: validation, worktree: true, fresh: true, feedback-to: implementation, gate: true}
    - {name: done, terminal: true}
---

# Yes to Relay URL Pilot Workflow

This repository-local workflow shapes one bounded Pilot product slice: a future high-level operation that offers a safe Relay review room for a finished identifiable artifact and publishes it only after an explicit Yes. This run ends at the `ideation` artifact-confirmation gate. Feature implementation and delivery are excluded.

## Local Profile

- Project context: repository `README.md`, `docs/architecture.md`, and Relay/runtime code at baseline `727f67ee18a5ff5038a6c5e2635f0140ba06c48c`.
- Work-item and execution-state authority: this workflow, via Spacedock controller commands.
- Iteration authority: Captain Kent's commission resolution for the single work item.
- Delivery authority: none in this run; `delivery_artifact_review=false`, `pr_delivery_selected=false`.
- Loader: `scripts/profile-contract-loader.py`; contracts root: `contracts/`.
- Route mapping: Pilot `shape -> build -> verify-deliver` maps to `ideation -> implementation -> validation`; `backlog` queues and `done` terminalizes.
- Captain Kent owns profile, scope, irreversibility, destructive action, merge, and release. FO owns controller state and gates. Ensign owns stage artifacts. Advice has no state authority.
- Implementation-exit observation is out of scope because this run stops before build.

## File Naming

Each work item is a flat Markdown file here. Stage artifacts live at repository-native paths in the assigned worktree and are named in the stage report and gate binding.

## Schema

Work-item frontmatter uses `id`, `title`, `status`, `source`, `started`, `completed`, `verdict`, `score`, `worktree`, `issue`, `pr`, and `mod-block`. `sd-b32` provides stable stored IDs.

## Stages

### `backlog`

Queue state before a selected profile enters work.

- **Inputs:** Captain mission and authority map.
- **Outputs:** One item-local `kc-dev-flow-work-profile/v2` receipt.
- **Good:** Exact Pilot route and explicit design-only boundary.
- **Bad:** A global profile, sidecar receipt, or parallel tracker.

### `ideation`

Pilot shape produces a reviewable architecture/UX design for the accepted explicit-Yes journey.

- **Inputs:** Exact work item, baseline repository, loader-emitted Pilot shape contract, and repository-derived Relay capabilities and limits.
- **Outputs:** Self-contained HTML architecture/UX flow; rendered PNG; concise product-rules/acceptance Markdown; stage report with paths, dimensions, capability evidence, and falsifiable verification.
- **Outputs:** Distinguish narrow trigger, fail-closed preflight, disclosures, explicit Yes, `create -> verify -> package -> publish -> Room -> safe URL + expiresAt`, and disable/revoke/future-hard-delete lifecycles.
- **Outputs:** Prove zero horizontal overflow, clipping, overlapping labels, and overlapping arrows; report screenshot dimensions.
- **Good:** One limited-user journey, actual constraints, readable hierarchy, explicit non-goals, and evidence able to fail.
- **Bad:** Runtime implementation, invented limits, vague assent, leaked secrets, disable/revoke called delete, or exact-second deletion claims.
- **Gate content:** Bind HTML, PNG, rules Markdown, and stage report bytes. Present scope, exclusions, capability and render evidence, then ask only whether to approve the design direction or revise it.

### `implementation`

Future Pilot build after separate Captain approval.

- **Inputs:** Approved design and Pilot build contract.
- **Outputs:** Runnable integrated slice, focused tests, diagnostics, and bounded recovery.
- **Good:** Minimal repository-native journey.
- **Bad:** Starting in this run or publishing Relay content.

### `validation`

Future independent Pilot verify-deliver stage.

- **Inputs:** Exact implementation revision and accepted journey.
- **Outputs:** Journey, recovery, duplicate, diagnostic, and data-safety evidence.
- **Good:** One bounded repair loop and honest residual obligations.
- **Bad:** Running now, pushing, opening a PR, merging, releasing, or deploying.
- **Gate content:** AC evidence and remaining promotion triggers.

### `done`

Terminal state after the selected route and delivery authority; unreachable in this design-only run.

## Workflow-specific rules

- Load only the vendored kernel, selected Pilot base, and current stage via the repository-local loader and exact item.
- Trigger only on an explicit request to review a finished identifiable artifact; ordinary questions, discussion, or the word review alone do not trigger.
- In every Hermes-managed Slack channel, offer Relay first with disclosures and do not upload during the offer.
- Preflight derives actual capability and limits and fails closed for sensitive, unsupported, unreadable, changed, or unknown-limit artifacts.
- Disclose bearer-capability access, immutable fixed revision, actual media/size/quota limits, actual `expiresAt`, 30-day default access expiry plus later sweep, no Slack owner/session secrets, and advisory-only feedback.
- Only clear Yes authorizes publication sequencing. Silence, emoji, and vague approval do not.
- Room disable, Briefing revoke/expiry, and future hard deletion are distinct. Hard deletion separately confirms artifact/Briefing/Results/Room-session scope, recoverability, and immediate-versus-queued behavior. Never call disable/revoke delete.
- No secrets, spend, destructive action, irreversibility, remote write, merge, release, or deploy authority is granted.

## Workflow State

Run `spacedock status --workflow-dir docs/yes-relay-url-workflow` from the repository root.

## Work item Template

New work items use controller creation, canonical fields, an item-local profile receipt, falsifiable acceptance criteria, and explicit exclusions.

## Commit Discipline

- Controller commands own item creation and frontmatter transitions; never hand-edit status.
- Commit at dispatch and gate boundaries.
- Stage artifacts and reports are authored in the assigned worktree.
