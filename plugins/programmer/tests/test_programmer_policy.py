#!/usr/bin/env python3
"""Regression tests for the optional Programmer guard policy.

Run: python plugins/programmer/tests/test_programmer_policy.py

Both bypasses covered here were live on 2026-08-22:

  * COMMAND_TOOLS still described the retired v0.2.0-alpha surface, so
    shell_session and live_shell - the two v2.0 tools that actually execute an
    arbitrary command string - never reached the destructive-command check,
    while four dead names occupied the set.
  * base_tool() did not normalize case, so mcp__programmer__Powershell matched
    no set and ran unguarded.

A guard that silently stops covering a tool looks exactly like a guard that is
working, which is why these assert the deny, not merely the code shape.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

POLICY_DIR = Path(__file__).resolve().parents[1] / "hooks" / "opt-in" / "shared" / "policy"
ADAPTER = Path(__file__).resolve().parents[1] / "hooks" / "opt-in" / "adapters" / "claude" / "hook_adapter.py"
sys.path.insert(0, str(POLICY_DIR))

import programmer_hook  # noqa: E402 - import follows portable path setup

DESTRUCTIVE = "rm -rf C:/important/data"

# The v2.0 surface, verified by a live MCP initialize + tools/list handshake.
LIVE_COMMAND_TOOLS = {"bash", "powershell", "wsl_run", "wsl_bg", "shell_session", "live_shell"}
RETIRED_TOOLS = {"run", "chain", "psession_run", "smart_exec"}


def decide(tool: str, args: dict) -> str:
    """Run the real adapter the way a host would, and read its decision."""
    payload = json.dumps({"tool_name": f"mcp__programmer__{tool}", "tool_input": args})
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(ADAPTER), "--event", "PreToolUse"],
        input=payload, capture_output=True, text=True, timeout=60, check=False,
    )
    out = (result.stdout or "").strip()
    if not out:
        return "allow"
    try:
        parsed = json.loads(out)
    except json.JSONDecodeError:
        return "allow"
    specific = parsed.get("hookSpecificOutput") or {}
    return specific.get("permissionDecision") or parsed.get("decision") or "allow"


class CommandToolCensus(unittest.TestCase):
    def test_covers_every_live_command_tool(self):
        missing = LIVE_COMMAND_TOOLS - programmer_hook.COMMAND_TOOLS
        self.assertEqual(missing, set(), f"command tools missing from the guard: {sorted(missing)}")

    def test_does_not_rely_on_retired_tools(self):
        stale = RETIRED_TOOLS & programmer_hook.COMMAND_TOOLS
        self.assertEqual(stale, set(), f"guard still lists retired tools: {sorted(stale)}")


class DestructiveCommandGuard(unittest.TestCase):
    def test_every_command_tool_denies_a_recursive_delete(self):
        for tool in sorted(LIVE_COMMAND_TOOLS):
            with self.subTest(tool=tool):
                self.assertEqual(decide(tool, {"command": DESTRUCTIVE}), "deny")

    def test_session_tools_are_guarded_through_their_action_shape(self):
        for tool in ("shell_session", "live_shell"):
            with self.subTest(tool=tool):
                self.assertEqual(decide(tool, {"action": "run", "command": DESTRUCTIVE}), "deny")

    def test_tool_name_casing_cannot_bypass_the_guard(self):
        for tool in ("Powershell", "POWERSHELL", "Shell_Session", "live_SHELL"):
            with self.subTest(tool=tool):
                self.assertEqual(decide(tool, {"command": DESTRUCTIVE}), "deny")

    def test_ordinary_build_command_is_not_denied(self):
        self.assertNotEqual(decide("bash", {"command": "cargo build --release"}), "deny")

    def test_recursive_delete_of_a_disposable_path_is_not_denied(self):
        self.assertNotEqual(decide("bash", {"command": "rm -rf target/"}), "deny")


class ServerKillGuard(unittest.TestCase):
    def test_killing_a_live_mcp_server_is_denied(self):
        self.assertEqual(decide("kill_process", {"name": "programmer.exe"}), "deny")


if __name__ == "__main__":
    unittest.main(verbosity=2)
