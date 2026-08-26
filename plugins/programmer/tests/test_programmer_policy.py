#!/usr/bin/env python3
"""Regression tests for the optional Programmer guard policy.

Run: python plugins/programmer/tests/test_programmer_policy.py

The coverage failures behind these regressions were live in the prior profile:

  * COMMAND_TOOLS carried retired names and omitted live command shapes.
  * The public one-off shell name was `bash` even though the server ran cmd.exe.
  * A disposable substring anywhere in a command allowed unsafe mixed targets.
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

DESTRUCTIVE = "rmdir /s C:\\important\\data"

# The v2.0 surface, verified by a live MCP initialize + tools/list handshake.
LIVE_COMMAND_TOOLS = {
    "cmd", "powershell", "shortcut", "wsl_run", "wsl_bg",
    "shell_session", "live_shell",
}
RETIRED_TOOLS = {"run", "chain", "psession_run", "smart_exec", "bash"}


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

    def test_shortcut_raw_command_list_is_guarded(self):
        self.assertEqual(
            decide("shortcut", {"mode": "run", "commands": ["echo ready", DESTRUCTIVE]}),
            "deny",
        )

    def test_tool_name_casing_cannot_bypass_the_guard(self):
        for tool in ("Powershell", "POWERSHELL", "Shell_Session", "live_SHELL"):
            with self.subTest(tool=tool):
                self.assertEqual(decide(tool, {"command": DESTRUCTIVE}), "deny")

    def test_ordinary_build_command_is_not_denied(self):
        self.assertNotEqual(decide("cmd", {"command": "cargo build --release"}), "deny")

    def test_malformed_non_delete_is_not_misclassified_as_a_delete(self):
        self.assertNotEqual(decide("cmd", {"command": 'echo "unfinished'}), "deny")

    def test_recursive_delete_of_disposable_paths_is_not_denied(self):
        commands = (
            "rmdir /s target",
            'RMDIR /S "C:\\work\\BUILD"',
            "rm -rf dist/",
            'Remove-Item -LiteralPath "C:\\work\\.cache" -Recurse -Force',
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertNotEqual(decide("cmd", {"command": command}), "deny")

    def test_mixed_safe_and_unsafe_targets_are_denied(self):
        commands = (
            "rmdir /s target C:\\important\\data",
            "rm -rf target/ C:/important/data",
            'Remove-Item -Path "dist","C:\\important" -Recurse -Force',
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(decide("cmd", {"command": command}), "deny")

    def test_disposable_substrings_are_not_treated_as_path_components(self):
        for command in ("rm -rf C:/important/targeted", "rmdir /s C:\\work\\distribution"):
            with self.subTest(command=command):
                self.assertEqual(decide("cmd", {"command": command}), "deny")

    def test_every_delete_in_a_chained_command_is_validated(self):
        commands = (
            'rmdir /s "target" & rmdir /s "C:\\important"',
            'rm -rf "build/" && rm -rf "C:/important/data"',
            'Remove-Item -Recurse -Force "tmp"; Remove-Item -Recurse -Force "C:\\important"',
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(decide("cmd", {"command": command}), "deny")

    def test_root_dot_parent_and_dynamic_targets_are_denied(self):
        commands = (
            "rmdir /s .",
            "rmdir /s ..",
            "rmdir /s C:\\",
            "rmdir /s %TEMP%",
            "rm -rf target/*",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(decide("cmd", {"command": command}), "deny")

    def test_ambiguous_wrapped_delete_is_denied(self):
        command = 'powershell -Command "Remove-Item -Recurse -Force target"'
        self.assertEqual(decide("cmd", {"command": command}), "deny")

    def test_powershell_remove_item_aliases_validate_every_target(self):
        commands = (
            "ri -Path target,C:\\important -Recurse -Force",
            "del target C:\\important -Recurse -Force",
            "rmdir -LiteralPath dist,C:\\important -Recurse -Force",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(decide("powershell", {"command": command}), "deny")


class ServerKillGuard(unittest.TestCase):
    def test_killing_a_live_mcp_server_is_denied(self):
        self.assertEqual(decide("kill_process", {"name": "programmer.exe"}), "deny")


if __name__ == "__main__":
    unittest.main(verbosity=2)
