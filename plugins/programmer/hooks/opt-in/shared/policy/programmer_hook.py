#!/usr/bin/env python3
"""Portable guard policy for optional Programmer-Wander hook templates.

Read-only against the payload; writes nothing but an audit line. Decisions:
  deny  - destructive command patterns, kills aimed at live MCP servers
  warn  - cargo via powershell, writes into protected config roots
  observe - everything else
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any

# Every v2.0 tool that can execute an arbitrary command string. Keep this list
# aligned with a live tools/list: a real command tool missing from it skips the
# destructive-command pre-flight entirely. The v2.0 rebuild retired run, chain,
# psession_run, smart_exec, and the misleading bash name. shell_session,
# live_shell, and shortcut also accept arbitrary commands and must be covered.
COMMAND_TOOLS = {
    "cmd", "powershell", "shortcut", "wsl_run", "wsl_bg",
    "shell_session", "live_shell",
}
WRITE_TOOLS = {
    "write_file", "edit_block", "move_file", "copy_file",
    "transform_find_replace", "transform_sync_dir", "transform_bulk_rename",
}
SERVER_EXES = (
    "programmer", "autonomous", "hands", "local", "manager",
    "workflow", "voice", "ops", "uniman",
)
DISPOSABLE_COMPONENTS = frozenset({
    "target", "build", "tmp", ".cache", "node_modules", "dist",
})

# These are detection hints, not parsers. A match that cannot be parsed into
# concrete targets is denied as ambiguous; an allowed delete must pass the
# per-target validation below.
RECURSIVE_DELETE_HINTS = (
    re.compile(
        r"\brm(?:\.exe)?\b(?=[^;&|\r\n]*\s-[^\s;&|]*r)"
        r"(?=[^;&|\r\n]*\s-[^\s;&|]*f)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:remove-item|ri|del|erase|rmdir|rd)\b"
        r"(?=[^;&|\r\n]*\s-recurse\b)"
        r"(?=[^;&|\r\n]*\s-force\b)",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:rmdir|rd|del|erase)(?:\.exe)?\b[^;&|\r\n]*\s/s\b",
               re.IGNORECASE),
)
FORCE_PUSH = re.compile(r"git\s+push\b.*(\s--force\b|\s-f\b)", re.IGNORECASE)
PROCESS_KILL = re.compile(r"(taskkill\b|stop-process\b|kill(all)?\s)", re.IGNORECASE)
DISK_DESTROY = re.compile(r"(format-volume|diskpart|cipher\s+/w|mkfs\.|format\s+[a-z]:)", re.IGNORECASE)
CARGO = re.compile(r"\b(cargo|rustc)\b", re.IGNORECASE)


def _split_shell_clauses(command: str) -> tuple[list[str], str]:
    """Split common shell command separators without splitting quoted text."""
    clauses: list[str] = []
    current: list[str] = []
    quote = ""
    escaped = False
    for char in command:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\" and quote:
            current.append(char)
            escaped = True
            continue
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
            current.append(char)
        elif char in ";&|\r\n":
            clause = "".join(current).strip()
            if clause:
                clauses.append(clause)
            current = []
        else:
            current.append(char)
    if quote:
        return [], "unclosed quote"
    clause = "".join(current).strip()
    if clause:
        clauses.append(clause)
    return clauses, ""


def _has_recursive_delete_hint(clause: str) -> bool:
    return any(pattern.search(clause) for pattern in RECURSIVE_DELETE_HINTS)


def _bare_token(token: str) -> str:
    return token.strip().strip("\"'")


def _command_name(token: str) -> str:
    value = _bare_token(token).replace("\\", "/").rsplit("/", 1)[-1].lower()
    return value[:-4] if value.endswith(".exe") else value


def _split_target_values(token: str) -> list[str]:
    """Split PowerShell comma path lists while respecting simple quotes."""
    values: list[str] = []
    current: list[str] = []
    quote = ""
    for char in token:
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
        elif char in ("'", '"'):
            quote = char
            current.append(char)
        elif char == ",":
            values.append("".join(current))
            current = []
        else:
            current.append(char)
    values.append("".join(current))
    return values


def _rm_targets(args: list[str]) -> tuple[list[str], str, bool]:
    flags = "".join(token[1:] for token in args if token.startswith("-") and token != "--")
    if "r" not in flags.lower() or "f" not in flags.lower():
        return [], "", False
    after_options = False
    targets = []
    for token in args:
        if token == "--":
            after_options = True
        elif not after_options and token.startswith("-"):
            continue
        else:
            targets.extend(_split_target_values(token))
    return targets, "", True


def _powershell_targets(args: list[str]) -> tuple[list[str], str, bool]:
    lowered = [_bare_token(token).lower() for token in args]
    if "-recurse" not in lowered or "-force" not in lowered:
        return [], "", False
    targets: list[str] = []
    index = 0
    while index < len(args):
        option = lowered[index]
        if option in ("-recurse", "-force", "-confirm:$false", "-whatif:$false"):
            index += 1
            continue
        if option in ("-path", "-literalpath"):
            if index + 1 >= len(args):
                return [], f"{option} has no value", True
            targets.extend(_split_target_values(args[index + 1]))
            index += 2
            continue
        if option.startswith("-"):
            return [], f"unsupported Remove-Item option {args[index]}", True
        targets.extend(_split_target_values(args[index]))
        index += 1
    return targets, "", True


def _cmd_targets(name: str, args: list[str]) -> tuple[list[str], str, bool]:
    lowered = [_bare_token(token).lower() for token in args]
    recursive = any(
        token.startswith("/") and "s" in token[1:].replace("/", "")
        for token in lowered
    )
    if not recursive:
        return [], "", False
    allowed_flags = set("sqfap") if name in ("del", "erase") else set("sq")
    targets: list[str] = []
    for raw, token in zip(args, lowered):
        if token.startswith("/") and len(token) > 1:
            letters = set(token[1:].replace("/", ""))
            if letters and letters <= allowed_flags:
                continue
        targets.extend(_split_target_values(raw))
    return targets, "", True


def _delete_operations(clause: str) -> tuple[list[list[str]], str]:
    try:
        tokens = shlex.split(clause, posix=False)
    except ValueError as exc:
        return [], str(exc)
    operations: list[list[str]] = []
    for index, token in enumerate(tokens):
        name = _command_name(token)
        args = tokens[index + 1:]
        if name in ("remove-item", "ri"):
            targets, error, recursive = _powershell_targets(args)
        elif name == "rm":
            targets, error, recursive = _powershell_targets(args)
            if not recursive and not error:
                targets, error, recursive = _rm_targets(args)
        elif name in ("rmdir", "rd", "del", "erase"):
            targets, error, recursive = _powershell_targets(args)
            if not recursive and not error:
                targets, error, recursive = _cmd_targets(name, args)
        else:
            continue
        if error:
            return [], error
        if recursive:
            operations.append(targets)
    return operations, ""


def _validate_delete_target(raw_target: str) -> tuple[bool, str]:
    target = _bare_token(raw_target).strip()
    if not target:
        return False, "empty target"
    if any(char in target for char in "$%!*?[]{}()`<>|;&\r\n"):
        return False, f"dynamic or wildcard target {target!r}"
    normalized = target.replace("\\", "/").rstrip("/")
    if normalized.lower() in ("", ".", "..", "~"):
        return False, f"root, dot, or parent target {target!r}"
    if re.fullmatch(r"[a-zA-Z]:", normalized):
        return False, f"drive-root target {target!r}"
    if normalized.startswith("//"):
        return False, f"UNC target {target!r}"
    components = [part.lower() for part in normalized.split("/") if part]
    if any(part in (".", "..", "~") for part in components):
        return False, f"dot or parent component in {target!r}"
    if not any(part in DISPOSABLE_COMPONENTS for part in components):
        return False, f"non-disposable target {target!r}"
    return True, ""


def validate_recursive_deletes(command: str) -> tuple[bool, str, bool]:
    """Validate every target of every recursive delete in a command string."""
    clauses, error = _split_shell_clauses(command)
    if error:
        if _has_recursive_delete_hint(command):
            return False, error, True
        return True, "", False
    saw_delete = False
    for clause in clauses:
        if not _has_recursive_delete_hint(clause):
            continue
        operations, parse_error = _delete_operations(clause)
        if parse_error:
            return False, parse_error, True
        if not operations:
            return False, "recursive delete could not be parsed into concrete targets", True
        saw_delete = True
        for targets in operations:
            if not targets:
                return False, "recursive delete has no concrete target", True
            for target in targets:
                allowed, target_error = _validate_delete_target(target)
                if not allowed:
                    return False, target_error, True
    return True, "", saw_delete


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    value = json.loads(raw)
    return value if isinstance(value, dict) else {}


def tool_name(payload: dict[str, Any]) -> str:
    for key in ("tool_name", "toolName", "name"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def base_tool(payload: dict[str, Any]) -> str:
    """Strip mcp__programmer__ style prefixes down to the bare tool name.

    Casefolded deliberately: the guard matches against lowercase sets, so an
    unnormalized name like mcp__programmer__Powershell missed every set and
    executed unguarded. Normalizing here closes that bypass for all callers.
    """
    return tool_name(payload).split("__")[-1].strip().lower()


def tool_args(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("tool_input", "toolInput", "arguments", "args"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def command_text(args: dict[str, Any]) -> str:
    parts = []
    for key in ("command", "cmd", "script", "commands"):
        value = args.get(key)
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
    return "\n".join(parts)


def protected_path(path: str) -> bool:
    lowered = path.replace("\\", "/").lower()
    home = str(Path.home()).replace("\\", "/").lower()
    roots = (
        f"{home}/.claude/", f"{home}/.codex/",
        "appdata/roaming/claude", "c:/cpc/config",
    )
    if any(root in lowered for root in roots):
        return True
    name = lowered.rsplit("/", 1)[-1]
    return name.startswith("operating_") or name == "cpc_state.json"


def emit_context(event: str, message: str) -> None:
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": event, "additionalContext": message}
    }, ensure_ascii=True))


def emit_deny(event: str, reason: str) -> None:
    sys.stdout.write(json.dumps({
        "decision": "deny",
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }, ensure_ascii=True))


def audit(event: str, host: str, payload: dict[str, Any], decision: str, detail: str) -> None:
    try:
        root = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "ProgrammerWander" / "hooks"
        root.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "event": event,
            "host": host,
            "tool": tool_name(payload),
            "decision": decision,
            "detail": detail,
        }
        with (root / "audit.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=True, sort_keys=True) + "\n")
    except OSError:
        pass


STREAK_WINDOW_SECONDS = 30 * 60
STREAK_THRESHOLD = 3


def _streak_state_path() -> Path:
    root = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "ProgrammerWander" / "hooks"
    root.mkdir(parents=True, exist_ok=True)
    return root / "failure_streaks.json"


def _fallback_map() -> dict[str, Any]:
    """Load the learned fallback map. CPC hosts point CPC_ERROR_FALLBACKS at the
    Volumes copy (default below); shipped users without a map get generic advice."""
    candidates = [
        os.environ.get("CPC_ERROR_FALLBACKS", ""),
        r"C:\My Drive\Volumes\logs\error_fallbacks.json",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            try:
                return json.loads(Path(candidate).read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
    return {}


def three_strike_advice(event: str, payload: dict[str, Any]) -> tuple[str, str]:
    """3-strike fallback hook (ratified 2026-07-29, replaces the retired tool_fallback
    tool): when the same tool+target fails 3 times inside the window, inject the
    recorded fallback from the learned map. Advisory only - never blocking."""
    tool = base_tool(payload)
    args = tool_args(payload)
    target = (command_text(args) or str(args.get("path", "")) or
              str(args.get("file_path", "")) or str(args.get("url", "")))[:120]
    key = f"{tool}|{target}"
    now = dt.datetime.now(dt.timezone.utc).timestamp()

    state_path = _streak_state_path()
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        state = {}
    # Expire stale streaks, bump this one
    state = {k: v for k, v in state.items()
             if isinstance(v, dict) and now - v.get("last", 0) < STREAK_WINDOW_SECONDS}
    entry = state.get(key, {"count": 0, "last": now})
    entry["count"] = int(entry.get("count", 0)) + 1
    entry["last"] = now
    state[key] = entry
    try:
        state_path.write_text(json.dumps(state, ensure_ascii=True), encoding="utf-8")
    except OSError:
        pass

    if entry["count"] < STREAK_THRESHOLD:
        return "observe", f"failure-streak {entry['count']}/{STREAK_THRESHOLD}"

    # Third strike: consult the learned map for a recorded fallback
    fallback_note = ""
    for name, rec in _fallback_map().items():
        if name.startswith("_") or not isinstance(rec, dict):
            continue
        trigger = str(rec.get("trigger", "")).lower()
        if trigger and (trigger in tool.lower() or tool.lower() in trigger):
            fallback_note = (f" Recorded fallback for this class ('{name}'): "
                             f"{rec.get('fallback', '?')}"
                             + (f" (symptom: {rec.get('symptom')})" if rec.get("symptom") else ""))
            break
    emit_context(event, f"'{tool}' has failed {entry['count']} times on the same target "
                        f"inside {STREAK_WINDOW_SECONDS // 60} minutes - stop retrying the "
                        f"same call.{fallback_note or ' No recorded fallback for this class; switch approach (different tool, powershell/cmd direct, or ask the user).'}"
                        " Run doctor to confirm this host actually has the capability.")
    return "warn", f"three-strike advisory ({entry['count']})"


def check_command(event: str, cmd: str) -> tuple[str, str]:
    """Return (decision, message) for a command string."""
    if DISK_DESTROY.search(cmd):
        return "deny", "Disk-destroying command pattern blocked by the Programmer guard hook."
    deletes_allowed, delete_error, saw_delete = validate_recursive_deletes(cmd)
    if saw_delete and not deletes_allowed:
        return ("deny",
                "Recursive delete denied: " + delete_error + ". Every target must be a "
                "concrete disposable path component (target, build, tmp, .cache, "
                "node_modules, or dist).")
    if FORCE_PUSH.search(cmd) and "--force-with-lease" not in cmd:
        return ("deny",
                "Bare force-push blocked. Use --force-with-lease, or have the user push.")
    if PROCESS_KILL.search(cmd) and any(exe in cmd.lower() for exe in SERVER_EXES):
        return ("deny",
                "Command appears to kill a running MCP server. Stage the change "
                "(.new + swap) and let the user restart at their boundary.")
    if CARGO.search(cmd):
        return ("warn-cargo", "")
    return "observe", ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--host", required=True, choices=("claude", "codex", "grok"))
    options = parser.parse_args()

    try:
        payload = read_payload()
    except (json.JSONDecodeError, OSError):
        return 0

    event = options.event
    decision, detail = "observe", ""

    if event == "SessionStart":
        emit_context(event, "Programmer-Wander guard hooks active: destructive commands, "
                            "server kills, and bare force-pushes are denied; writes to "
                            "protected config roots get an archive-first reminder.")
    elif event == "PreToolUse":
        tool = base_tool(payload)
        args = tool_args(payload)
        if tool in COMMAND_TOOLS:
            cmd = command_text(args)
            decision, message = check_command(event, cmd)
            if decision == "deny":
                detail = message
                audit(event, options.host, payload, decision, detail)
                emit_deny(event, message)
                return 0
            if decision == "warn-cargo" and tool == "powershell":
                decision, detail = "warn", "cargo-via-powershell"
                emit_context(event, "cargo/rustc through the powershell tool corrupts piped "
                                    "output. Use the cmd tool for cargo work.")
        elif tool == "kill_process":
            target = str(args.get("name", "")) + " " + str(args.get("process", ""))
            if any(exe in target.lower() for exe in SERVER_EXES):
                decision = "deny"
                detail = "kill_process on MCP server"
                audit(event, options.host, payload, decision, detail)
                emit_deny(event, "kill_process target looks like a live MCP server. Verify with "
                                 "server_health; stage a swap instead of killing it mid-session.")
                return 0
        elif tool in WRITE_TOOLS:
            paths = " ".join(str(args.get(key, "")) for key in
                             ("path", "file_path", "destination", "target", "source"))
            if protected_path(paths):
                decision, detail = "warn", "write-to-protected-root"
                emit_context(event, "Target is under a protected config root. Archive-first: "
                                    "copy the current version to a backups dir before overwriting.")
    elif event == "PostToolUseFailure":
        decision, detail = three_strike_advice(event, payload)

    audit(event, options.host, payload, decision, detail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
