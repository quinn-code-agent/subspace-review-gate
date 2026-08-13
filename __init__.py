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


def schema(name, description, properties, required):
    return {"name": name, "description": description, "parameters": {"type": "object", "properties": properties, "required": required}}


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
