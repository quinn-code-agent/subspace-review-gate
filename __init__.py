"""Hermes plugin registration for Subspace Review & Gate v1 helpers."""
from __future__ import annotations

import hashlib
import json
import os
import fcntl
import shlex
import stat
import subprocess
import sys
import tempfile
import time
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
    if args.get("endpoint"): command.extend(["--endpoint", args["endpoint"]])
    if args.get("state_dir"): command.extend(["--state-dir", args["state_dir"]])
    return relay_call(*command)


def relay_pull_result(args, **_):
    command = ["pull-result", "--briefing", args["briefing"], "--result-id", args["result_id"], "--output-dir", args["output_dir"]]
    if args.get("endpoint"): command.extend(["--endpoint", args["endpoint"]])
    if args.get("state_dir"): command.extend(["--state-dir", args["state_dir"]])
    return relay_call(*command)


def relay_create_room(args, **_):
    command = ["create-room", "--briefing", args["briefing"]]
    if args.get("endpoint"): command.extend(["--endpoint", args["endpoint"]])
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


def relay_share_consented(args, **_):
    command = [
        "share-consented", "--artifact", args["artifact"], "--question", args["question"],
        "--briefing", args["briefing"], "--package", args["package"],
        "--consent", args["consent"], "--consented-revision", args["consented_revision"],
        "--audience", args["audience"], "--media-type", args["media_type"],
        "--sensitivity", args["sensitivity"], "--state-dir", args["state_dir"],
    ]
    if args.get("endpoint"): command.extend(["--endpoint", args["endpoint"]])
    return relay_call(*command)


_WATCHER_PROCESSES = {}


def _write_private_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(data, stream, indent=2); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try: os.close(fd)
        except OSError: pass
        try: os.unlink(temporary)
        except OSError: pass
        raise


def _read_private_json(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
        raise ValueError("watcher process state must have private permissions (0600)")
    return json.loads(path.read_text())


def _watcher_ref(briefing, room_ref):
    return "watcher_" + hashlib.sha256(f"{briefing}\0{room_ref}".encode()).hexdigest()[:20]


def _pid_is_watcher(record):
    pid = record.get("pid")
    binding = record.get("binding")
    token = record.get("watcher_token")
    ready_file = record.get("ready_file")
    if not isinstance(pid, int) or not isinstance(binding, dict) or not isinstance(token, str) or not isinstance(ready_file, str):
        return False
    try:
        os.kill(pid, 0)
        command = subprocess.run(["/bin/ps", "-ww", "-p", str(pid), "-o", "command="], text=True, capture_output=True, check=True).stdout
        argv = shlex.split(command)
    except (OSError, ValueError):
        return False
    except (subprocess.SubprocessError, IndexError):
        return False
    expected = {
        "--briefing": binding.get("briefing"), "--room-ref": binding.get("room_ref"),
        "--origin-channel": binding.get("origin_channel"), "--origin-thread": binding.get("origin_thread"),
        "--outbox": binding.get("outbox"), "--state-dir": binding.get("state_dir"),
        "--ready-file": ready_file, "--watcher-token": token,
    }
    if str(ROOT / "bin" / "subspace-review-relay") not in argv or "watch-feedback" not in argv:
        return False
    for flag, value in expected.items():
        try:
            if argv[argv.index(flag) + 1] != value:
                return False
        except (ValueError, IndexError):
            return False
    try:
        interval_matches = float(argv[argv.index("--interval") + 1]) == binding.get("interval")
    except (ValueError, IndexError):
        return False
    return interval_matches and (("--first-valid" in argv) == binding.get("first_valid"))


def _pid_exists(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except (PermissionError, TypeError, ValueError):
        return True


def _wait_until_not_watcher(record, timeout):
    process = _WATCHER_PROCESSES.get(record.get("pid"))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process is not None:
            if process.poll() is not None:
                process.wait()
                return True
        elif not _pid_is_watcher(record):
            return not _pid_exists(record.get("pid"))
        time.sleep(0.025)
    return not _pid_exists(record.get("pid"))


def relay_watch_feedback(args, **_):
    state = Path(args["state_dir"]).expanduser().resolve()
    logs = state / "watchers" / "logs"
    processes = state / "watchers" / "processes"
    ready_dir = state / "watchers" / "ready"
    for directory in (logs, processes, ready_dir): directory.mkdir(parents=True, exist_ok=True)
    watcher_ref = _watcher_ref(args["briefing"], args["room_ref"])
    binding = {"briefing": args["briefing"], "room_ref": args["room_ref"],
               "origin_channel": args["origin_channel"], "origin_thread": args["origin_thread"],
               "outbox": str(Path(args["outbox"]).expanduser().resolve()),
               "state_dir": str(state),
               "first_valid": bool(args.get("first_valid")), "interval": float(args.get("interval", 15))}
    process_path = processes / f"{watcher_ref}.json"
    ready_path = ready_dir / f"{watcher_ref}.json"
    lock_path = processes / f"{watcher_ref}.lock"
    lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        os.fchmod(lock_fd, 0o600)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        if process_path.exists():
            try: record = _read_private_json(process_path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                return json.dumps({"ok": False, "error": str(exc)})
            if record.get("binding") != binding:
                return json.dumps({"ok": False, "error": "watcher binding is immutable; rebinding refused"})
            pid = record.get("pid")
            if isinstance(pid, int) and _pid_is_watcher(record):
                return json.dumps({"ok": True, "watcher_ref": watcher_ref, "background": True,
                                   "pid": pid, "ready": True, "reused": True})
            process_path.unlink(missing_ok=True); ready_path.unlink(missing_ok=True)
        ready_path.unlink(missing_ok=True)
        stop_path = state / "watchers" / args["briefing"] / f"{args['room_ref']}.stop"
        stop_path.unlink(missing_ok=True)
        watcher_token = hashlib.sha256(os.urandom(32)).hexdigest()
        command = [
            sys.executable, str(ROOT / "bin" / "subspace-review-relay"), "watch-feedback",
            "--briefing", args["briefing"], "--room-ref", args["room_ref"],
            "--origin-channel", args["origin_channel"], "--origin-thread", args["origin_thread"],
            "--outbox", binding["outbox"], "--state-dir", str(state),
            "--interval", str(binding["interval"]), "--ready-file", str(ready_path),
            "--watcher-token", watcher_token,
        ]
        if binding["first_valid"]: command.append("--first-valid")
        stdout_path = logs / f"{watcher_ref}.out"; stderr_path = logs / f"{watcher_ref}.err"
        stdout_fd = os.open(stdout_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        stderr_fd = os.open(stderr_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        os.fchmod(stdout_fd, 0o600); os.fchmod(stderr_fd, 0o600)
        with os.fdopen(stdout_fd, "ab") as stdout, os.fdopen(stderr_fd, "ab") as stderr:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
        _WATCHER_PROCESSES[process.pid] = process
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not ready_path.exists() and process.poll() is None:
            time.sleep(0.025)
        record = {"version": 1, "watcher_ref": watcher_ref, "pid": process.pid, "binding": binding,
                  "watcher_token": watcher_token, "ready_file": str(ready_path)}
        if not ready_path.exists() or process.poll() is not None:
            if process.poll() is None and _pid_is_watcher(record):
                process.terminate(); process.wait(timeout=2)
            _WATCHER_PROCESSES.pop(process.pid, None)
            return json.dumps({"ok": False, "error": "feedback watcher failed readiness check"})
        ready = _read_private_json(ready_path)
        expected_ready = {"version": 1, "pid": process.pid, "watcherToken": watcher_token,
                          "briefing": binding["briefing"], "roomRef": binding["room_ref"],
                          "binding": {"origin": {"channel": binding["origin_channel"], "thread": binding["origin_thread"]},
                                      "outbox": binding["outbox"]}}
        if ready != expected_ready or not _pid_is_watcher(record):
            if _pid_is_watcher(record):
                process.terminate(); process.wait(timeout=2)
            _WATCHER_PROCESSES.pop(process.pid, None)
            ready_path.unlink(missing_ok=True)
            return json.dumps({"ok": False, "error": "feedback watcher returned an invalid readiness marker"})
        _write_private_json(process_path, record)
        return json.dumps({"ok": True, "watcher_ref": watcher_ref, "background": True,
                           "pid": process.pid, "ready": True, "reused": False})
    finally:
        os.close(lock_fd)


def relay_stop_feedback_watch(args, **_):
    state = Path(args["state_dir"]).expanduser().resolve()
    watcher_ref = _watcher_ref(args["briefing"], args["room_ref"])
    processes = state / "watchers" / "processes"
    process_path = processes / f"{watcher_ref}.json"
    lock_path = processes / f"{watcher_ref}.lock"
    processes.mkdir(parents=True, exist_ok=True)
    lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        os.fchmod(lock_fd, 0o600)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        record = None
        if process_path.exists():
            try:
                candidate = _read_private_json(process_path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                return json.dumps({"ok": False, "shutdown_verified": False, "error": str(exc)})
            binding = candidate.get("binding", {})
            if (candidate.get("watcher_ref") != watcher_ref or binding.get("briefing") != args["briefing"]
                    or binding.get("room_ref") != args["room_ref"] or binding.get("state_dir") != str(state)):
                return json.dumps({"ok": False, "shutdown_verified": False,
                                   "error": "stored watcher identity does not match the requested binding"})
            record = candidate
        payload = relay_call("stop-feedback-watch", "--briefing", args["briefing"],
                             "--room-ref", args["room_ref"], "--state-dir", str(state))
        try:
            marker_result = json.loads(payload)
        except json.JSONDecodeError:
            return payload
        if record is None:
            return json.dumps({**marker_result, "shutdown_verified": False,
                               "error": "no durable watcher process identity was available"})
        pid = record["pid"]
        if not _wait_until_not_watcher(record, max(0.5, min(record["binding"]["interval"] + 0.5, 2.0))):
            # Re-prove the complete durable binding immediately before signalling.
            if not _pid_is_watcher(record):
                return json.dumps({**marker_result, "pid": pid, "shutdown_verified": False,
                                   "error": "stored PID no longer identifies this watcher; no signal was sent"})
            os.kill(pid, 15)
        shutdown_verified = _wait_until_not_watcher(record, 2.0)
        if shutdown_verified:
            process_path.unlink(missing_ok=True)
            Path(record["ready_file"]).unlink(missing_ok=True)
            _WATCHER_PROCESSES.pop(pid, None)
        return json.dumps({**marker_result, "pid": pid, "shutdown_verified": shutdown_verified,
                           "state": "stopped" if shutdown_verified else "stop-requested"})
    finally:
        os.close(lock_fd)


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
    relay_endpoint = {"endpoint": {"type": "string", "description": "Relay base URL; defaults to the shared staging endpoint."}}
    ctx.register_tool(name="subspace_review_gate_relay_package", toolset="subspace_review_gate", emoji="📦", check_fn=available,
        schema=schema("subspace_review_gate_relay_package", "Build a Relay-compatible package from a verified immutable Briefing. Phase 1 feedback transport only.", {**common, "output_dir": {"type": "string"}}, ["briefing", "output_dir"]), handler=relay_package)
    ctx.register_tool(name="subspace_review_gate_relay_publish", toolset="subspace_review_gate", emoji="🚀", check_fn=available,
        schema=schema("subspace_review_gate_relay_publish", "Publish a Relay package to staging and store a local private owner receipt. Does not create a Resolution.", {"package": {"type": "string"}, **relay_endpoint, "state_dir": {"type": "string"}}, ["package"]), handler=relay_publish)
    ctx.register_tool(name="subspace_review_gate_relay_fetch", toolset="subspace_review_gate", emoji="📥", check_fn=available,
        schema=schema("subspace_review_gate_relay_fetch", "Fetch and SHA-256 verify a shared Relay package for a Web or TUI viewer. Feedback-only Phase 1.", {**common, "output_dir": {"type": "string"}, **relay_endpoint}, ["briefing", "output_dir"]), handler=relay_fetch)
    ctx.register_tool(name="subspace_review_gate_relay_annotations", toolset="subspace_review_gate", emoji="📝", check_fn=available,
        schema=schema("subspace_review_gate_relay_annotations", "Convert Human Review comments to portable Subspace Annotation JSONL; no Resolution is emitted.", {**common, "feedback": {"type": "string"}, "output": {"type": "string"}, "reviewer": {"type": "string"}}, ["briefing", "feedback", "output"]), handler=relay_annotations)
    ctx.register_tool(name="subspace_review_gate_relay_results", toolset="subspace_review_gate", emoji="📨", check_fn=available,
        schema=schema("subspace_review_gate_relay_results", "Owner-only pull of Relay Result summaries. Results remain feedback-only evidence and do not route a workflow.", {**common, **relay_endpoint, "state_dir": {"type": "string"}}, ["briefing"]), handler=relay_results)
    ctx.register_tool(name="subspace_review_gate_relay_pull_result", toolset="subspace_review_gate", emoji="📥", check_fn=available,
        schema=schema("subspace_review_gate_relay_pull_result", "Owner-only pull of one feedback-only Relay Result: validates its Briefing and mode, then reports SHA-256 digests. This does not create a Resolution or change workflow state.", {**common, "result_id": {"type": "string"}, "output_dir": {"type": "string"}, **relay_endpoint, "state_dir": {"type": "string", "description": "Optional private owner-receipt directory."}}, ["briefing", "result_id", "output_dir"]), handler=relay_pull_result)
    room_props = {**common, **relay_endpoint, "state_dir": {"type": "string", "description": "Optional private owner-receipt directory."}}
    ctx.register_tool(name="subspace_review_gate_relay_create_room", toolset="subspace_review_gate", emoji="🏠", check_fn=available,
        schema=schema("subspace_review_gate_relay_create_room", "Create a Relay Review Room for an already-published Briefing using its private owner receipt. This does not create an invitation or a Resolution.", room_props, ["briefing"]), handler=relay_create_room)
    ctx.register_tool(name="subspace_review_gate_relay_disable_room", toolset="subspace_review_gate", emoji="🛑", check_fn=available,
        schema=schema("subspace_review_gate_relay_disable_room", "Disable a Relay Review Room using its private non-network room reference and owner receipt. This does not expose the Room capability or write a workflow verdict.", {**common, "room_ref": {"type": "string"}, "state_dir": {"type": "string", "description": "Optional private owner-receipt directory."}}, ["briefing", "room_ref"]), handler=relay_disable_room)
    ctx.register_tool(name="subspace_review_gate_relay_revoke_room_session", toolset="subspace_review_gate", emoji="🚫", check_fn=available,
        schema=schema("subspace_review_gate_relay_revoke_room_session", "Revoke one arrived reviewer session using a private non-network Room reference and owner receipt. This does not expose a Room capability or write workflow state.", {**common, "room_ref": {"type": "string"}, "session_id": {"type": "string"}, "state_dir": {"type": "string", "description": "Optional private owner-receipt directory."}}, ["briefing", "room_ref", "session_id"]), handler=relay_revoke_room_session)
    share_props = {
        "artifact": {"type": "string"}, "question": {"type": "string"}, "briefing": {"type": "string"},
        "package": {"type": "string"}, "consent": {"type": "string", "description": "The clear affirmative reply to the disclosed offer."},
        "consented_revision": {"type": "string"}, "audience": {"type": "string"}, "media_type": {"type": "string"},
        "sensitivity": {"type": "string", "enum": ["non-sensitive", "sensitive", "unknown"]},
        **relay_endpoint, "state_dir": {"type": "string", "description": "Private operation and owner-state directory."},
    }
    ctx.register_tool(name="subspace_review_gate_relay_share_consented", toolset="subspace_review_gate", emoji="🔗", check_fn=available,
        schema=schema("subspace_review_gate_relay_share_consented", "After one clear Yes, fail-closed preflight, create, verify, package, publish, and create a Room; returns only the safe Room URL and authoritative expiresAt.", share_props, ["artifact", "question", "consent", "consented_revision", "audience", "media_type", "sensitivity", "briefing", "package", "state_dir"]), handler=relay_share_consented)
    watch_props = {**common, "room_ref": {"type": "string"}, "origin_channel": {"type": "string"}, "origin_thread": {"type": "string"}, "outbox": {"type": "string"}, "state_dir": {"type": "string"}, "interval": {"type": "number"}, "first_valid": {"type": "boolean"}}
    ctx.register_tool(name="subspace_review_gate_relay_watch_feedback", toolset="subspace_review_gate", emoji="👀", check_fn=available,
        schema=schema("subspace_review_gate_relay_watch_feedback", "Start a Room-scoped background feedback watcher bound to the dispatch-origin Slack thread. It emits only a safe advisory event and does not advance workflow state.", watch_props, ["briefing", "room_ref", "origin_channel", "origin_thread", "outbox", "state_dir"]), handler=relay_watch_feedback)
    ctx.register_tool(name="subspace_review_gate_relay_stop_feedback_watch", toolset="subspace_review_gate", emoji="⏹️", check_fn=available,
        schema=schema("subspace_review_gate_relay_stop_feedback_watch", "Persist an explicit user-stop marker for a Room feedback watcher.", {**common, "room_ref": {"type": "string"}, "state_dir": {"type": "string"}}, ["briefing", "room_ref", "state_dir"]), handler=relay_stop_feedback_watch)
