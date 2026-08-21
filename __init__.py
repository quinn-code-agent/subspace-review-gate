"""Hermes plugin registration for Subspace Review & Gate v1 helpers."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLI = ROOT / "bin" / "subspace-review-gate"


def available():
    return CLI.is_file()


def call(*args):
    result = subprocess.run([sys.executable, str(CLI), *args], text=True, capture_output=True)
    if result.returncode:
        return json.dumps({"ok": False, "error": result.stderr.strip() or "review-gate command failed"})
    try:
        return result.stdout if result.stdout.lstrip().startswith("{") else json.dumps({"ok": True, "output": result.stdout.strip()})
    except Exception:
        return json.dumps({"ok": True, "output": result.stdout.strip()})


def create(args, **_):
    command = ["create", "--artifact", args["artifact"], "--question", args["question"], "--briefing", args["briefing"]]
    for route in args.get("routes", []):
        command.extend(["--route", route])
    return call(*command)


def verify(args, **_):
    return call("verify", "--briefing", args["briefing"])


def render_slack(args, **_):
    command = ["render-slack", "--briefing", args["briefing"]]
    if args.get("human_review_url"):
        command.extend(["--human-review-url", args["human_review_url"]])
    return call(*command)


def build_resolution(args, **_):
    command = ["build-resolution", "--briefing", args["briefing"], "--choice", args["choice"]]
    if args.get("reason"):
        command.extend(["--reason", args["reason"]])
    if args.get("by"):
        command.extend(["--by", args["by"]])
    return call(*command)


def runtime_call(*args):
    runtime = ROOT / "bin" / "subspace-review-runtime"
    result = subprocess.run([sys.executable, str(runtime), *args], text=True, capture_output=True)
    return result.stdout if result.stdout.strip() else json.dumps({"ok": False, "error": result.stderr.strip() or "review runtime failed"})


def open_public_review(args, **_):
    command = ["open", "--artifact", args["artifact"]]
    if args.get("state_dir"):
        command.extend(["--state-dir", args["state_dir"]])
    return runtime_call(*command)


def review_runtime_status(args, **_):
    command = ["status"]
    if args.get("state_dir"):
        command.extend(["--state-dir", args["state_dir"]])
    return runtime_call(*command)


def close_public_review(args, **_):
    command = ["close"]
    if args.get("state_dir"):
        command.extend(["--state-dir", args["state_dir"]])
    return runtime_call(*command)


def relay_call(*args):
    relay = ROOT / "bin" / "subspace-review-relay"
    result = subprocess.run([sys.executable, str(relay), *args], text=True, capture_output=True)
    return result.stdout if result.stdout.strip() else json.dumps({"ok": False, "error": result.stderr.strip() or "relay adapter failed"})


def relay_package(args, **_):
    return relay_call("package", "--briefing", args["briefing"], "--output-dir", args["output_dir"])


def relay_publish(args, **_):
    command = ["publish", "--package", args["package"]]
    if args.get("endpoint"): command.extend(["--endpoint", args["endpoint"]])
    if args.get("state_dir"): command.extend(["--state-dir", args["state_dir"]])
    return relay_call(*command)


def relay_fetch(args, **_):
    command = ["fetch", "--briefing", args["briefing"], "--output-dir", args["output_dir"]]
    if args.get("endpoint"): command.extend(["--endpoint", args["endpoint"]])
    return relay_call(*command)


def relay_annotations(args, **_):
    command = ["annotations", "--briefing", args["briefing"], "--feedback", args["feedback"], "--output", args["output"]]
    if args.get("reviewer"): command.extend(["--reviewer", args["reviewer"]])
    return relay_call(*command)


def relay_results(args, **_):
    command = ["results", "--briefing", args["briefing"]]
    if args.get("state_dir"): command.extend(["--state-dir", args["state_dir"]])
    return relay_call(*command)


def relay_owner_inbox(args, **_):
    command = ["owner-inbox", "--briefing", args["briefing"], "--output", args["output"]]
    if args.get("state_dir"): command.extend(["--state-dir", args["state_dir"]])
    return relay_call(*command)


def relay_pull_result(args, **_):
    command = ["pull-result", "--briefing", args["briefing"], "--result-id", args["result_id"], "--output-dir", args["output_dir"]]
    if args.get("state_dir"): command.extend(["--state-dir", args["state_dir"]])
    return relay_call(*command)


def relay_create_room(args, **_):
    command = ["create-room", "--briefing", args["briefing"]]
    if args.get("state_dir"): command.extend(["--state-dir", args["state_dir"]])
    return relay_call(*command)


def relay_disable_room(args, **_):
    command = ["disable-room", "--briefing", args["briefing"], "--room-ref", args["room_ref"]]
    if args.get("state_dir"): command.extend(["--state-dir", args["state_dir"]])
    return relay_call(*command)


def relay_revoke_room_session(args, **_):
    command = ["revoke-room-session", "--briefing", args["briefing"], "--room-ref", args["room_ref"], "--session-id", args["session_id"]]
    if args.get("state_dir"): command.extend(["--state-dir", args["state_dir"]])
    return relay_call(*command)


def schema(name, description, properties, required):
    return {"name": name, "description": description, "parameters": {"type": "object", "properties": properties, "required": required, "additionalProperties": False}}


def register(ctx):
    common = {"briefing": {"type": "string", "description": "Path to immutable Subspace v1 Briefing JSON."}}
    ctx.register_tool(name="subspace_review_gate_create", toolset="subspace_review_gate", emoji="🧭", check_fn=available,
        schema=schema("subspace_review_gate_create", "Create immutable Subspace v1 Briefing JSON for a fixed artifact revision.", {"artifact": {"type": "string"}, "question": {"type": "string"}, "briefing": {"type": "string"}, "routes": {"type": "array", "items": {"type": "string"}, "description": "Ordered decision|label|destination routes."}}, ["artifact", "question", "briefing"]), handler=create)
    ctx.register_tool(name="subspace_review_gate_verify", toolset="subspace_review_gate", emoji="✅", check_fn=available,
        schema=schema("subspace_review_gate_verify", "Verify each Briefing artifact still matches its raw-byte SHA-256 revision.", common, ["briefing"]), handler=verify)
    ctx.register_tool(name="subspace_review_gate_render_slack", toolset="subspace_review_gate", emoji="💬", check_fn=available,
        schema=schema("subspace_review_gate_render_slack", "Render ordered Subspace routes for Slack with reply-by-number instruction.", {**common, "human_review_url": {"type": "string"}}, ["briefing"]), handler=render_slack)
    ctx.register_tool(name="subspace_review_gate_build_resolution", toolset="subspace_review_gate", emoji="⚖️", check_fn=available,
        schema=schema("subspace_review_gate_build_resolution", "Validate one selected route and produce portable Subspace Annotation plus Resolution objects.", {**common, "choice": {"type": "string"}, "reason": {"type": "string"}, "by": {"type": "string"}}, ["briefing", "choice"]), handler=build_resolution)
    runtime_props = {"state_dir": {"type": "string", "description": "Optional directory for public-review process state."}}
    ctx.register_tool(name="subspace_review_gate_open_public_review", toolset="subspace_review_gate", emoji="🌐", check_fn=available,
        schema=schema("subspace_review_gate_open_public_review", "Open a temporary public HTTPS Human Review URL for an artifact and verify the live session. Anyone with the URL can submit feedback.", {"artifact": {"type": "string"}, **runtime_props}, ["artifact"]), handler=open_public_review)
    ctx.register_tool(name="subspace_review_gate_review_status", toolset="subspace_review_gate", emoji="📡", check_fn=available,
        schema=schema("subspace_review_gate_review_status", "Check whether the managed public Human Review proxy and tunnel are live.", runtime_props, []), handler=review_runtime_status)
    ctx.register_tool(name="subspace_review_gate_close_public_review", toolset="subspace_review_gate", emoji="🛑", check_fn=available,
        schema=schema("subspace_review_gate_close_public_review", "Stop the managed public Human Review proxy and temporary Cloudflare tunnel.", runtime_props, []), handler=close_public_review)
    relay_endpoint = {"endpoint": {"type": "string", "description": "Relay base URL; defaults to the shared staging endpoint."}}
    owner_common = {"briefing": {"type": "string", "description": "Briefing ID (briefing:<32 lowercase hex>), not a file path."}, "state_dir": {"type": "string", "description": "Optional private owner-receipt directory."}}
    ctx.register_tool(name="subspace_review_gate_relay_package", toolset="subspace_review_gate", emoji="📦", check_fn=available,
        schema=schema("subspace_review_gate_relay_package", "Build a Relay-compatible package from a verified immutable Briefing. Phase 1 feedback transport only.", {**common, "output_dir": {"type": "string"}}, ["briefing", "output_dir"]), handler=relay_package)
    ctx.register_tool(name="subspace_review_gate_relay_publish", toolset="subspace_review_gate", emoji="🚀", check_fn=available,
        schema=schema("subspace_review_gate_relay_publish", "Publish a Relay package to staging and store a local private owner receipt. Does not create a Resolution.", {"package": {"type": "string"}, **relay_endpoint, "state_dir": {"type": "string"}}, ["package"]), handler=relay_publish)
    ctx.register_tool(name="subspace_review_gate_relay_fetch", toolset="subspace_review_gate", emoji="📥", check_fn=available,
        schema=schema("subspace_review_gate_relay_fetch", "Fetch and SHA-256 verify a shared Relay package for a Web or TUI viewer. Feedback-only Phase 1.", {**common, "output_dir": {"type": "string"}, **relay_endpoint}, ["briefing", "output_dir"]), handler=relay_fetch)
    ctx.register_tool(name="subspace_review_gate_relay_annotations", toolset="subspace_review_gate", emoji="📝", check_fn=available,
        schema=schema("subspace_review_gate_relay_annotations", "Convert Human Review comments to portable Subspace Annotation JSONL; no Resolution is emitted.", {**common, "feedback": {"type": "string"}, "output": {"type": "string"}, "reviewer": {"type": "string"}}, ["briefing", "feedback", "output"]), handler=relay_annotations)
    ctx.register_tool(name="subspace_review_gate_relay_results", toolset="subspace_review_gate", emoji="📨", check_fn=available,
        schema=schema("subspace_review_gate_relay_results", "Owner-only structural Relay Result summaries. Reviewer free text is withheld from agent context; attribution remains self-declared and non-binding.", owner_common, ["briefing"]), handler=relay_results)
    ctx.register_tool(name="subspace_review_gate_relay_owner_inbox", toolset="subspace_review_gate", emoji="🗂️", check_fn=available,
        schema=schema("subspace_review_gate_relay_owner_inbox", "Write a private local 0600 human-facing HTML snapshot of validated Relay feedback. The tool response never contains reviewer labels or comments.", {**owner_common, "output": {"type": "string", "description": "Local HTML file path; written atomically and kept private."}}, ["briefing", "output"]), handler=relay_owner_inbox)
    ctx.register_tool(name="subspace_review_gate_relay_pull_result", toolset="subspace_review_gate", emoji="📥", check_fn=available,
        schema=schema("subspace_review_gate_relay_pull_result", "Owner-only pull of one validated coherent feedback-only Relay Result; computes local SHA-256 digests. This does not create a Resolution or change workflow state.", {**owner_common, "result_id": {"type": "string"}, "output_dir": {"type": "string"}}, ["briefing", "result_id", "output_dir"]), handler=relay_pull_result)
    room_props = owner_common
    ctx.register_tool(name="subspace_review_gate_relay_create_room", toolset="subspace_review_gate", emoji="🏠", check_fn=available,
        schema=schema("subspace_review_gate_relay_create_room", "Create a Relay Review Room for an already-published Briefing using its private owner receipt. This does not create an invitation or a Resolution.", room_props, ["briefing"]), handler=relay_create_room)
    ctx.register_tool(name="subspace_review_gate_relay_disable_room", toolset="subspace_review_gate", emoji="🛑", check_fn=available,
        schema=schema("subspace_review_gate_relay_disable_room", "Disable a Relay Review Room using its private non-network room reference and owner receipt. This does not expose the Room capability or write a workflow verdict.", {**owner_common, "room_ref": {"type": "string"}}, ["briefing", "room_ref"]), handler=relay_disable_room)
    ctx.register_tool(name="subspace_review_gate_relay_revoke_room_session", toolset="subspace_review_gate", emoji="🚫", check_fn=available,
        schema=schema("subspace_review_gate_relay_revoke_room_session", "Revoke one arrived reviewer session using a private non-network Room reference and owner receipt. This does not expose a Room capability or write workflow state.", {**owner_common, "room_ref": {"type": "string"}, "session_id": {"type": "string"}}, ["briefing", "room_ref", "session_id"]), handler=relay_revoke_room_session)
