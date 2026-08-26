---
name: programmer-safe-ops
description: Safety discipline for Programmer-Wander's powerful tools - command pre-flight, archive-first overwrites, staged binary swaps, process-kill hygiene, and audit trail. Surface before destructive commands, before overwriting configs or binaries, before kill_process, before deploys, and when a security warning or blocked command appears.
---

# Programmer Safe Ops

Programmer is a full dev shell. These rules keep it reversible.

## Command pre-flight

Command-entry tools (`cmd`, `powershell`, `shortcut`, `shell_session`,
`live_shell`, `wsl_run`, `wsl_bg`) pass through `security_check_cmd`
automatically. Critical destructive patterns are blocked and logged; recursive
deletes must use concrete targets whose path contains an obviously disposable
component (`target`, `build`, `tmp`, `.cache`, `node_modules`, or `dist`). Every
target is checked; mixed safe and unsafe targets, roots, traversal, variables,
and wildcards are blocked. To check a command before running it, call `security_check_cmd`
directly. Review decisions with `security_audit_log`.

## Archive-first

Before replacing any working file, config, or binary: copy the current version
aside (`copy_file` to a backups dir with a date suffix). An overwrite you can
roll back is an experiment; one you cannot is an incident.

## Staged swaps - never hot-swap a running server

A running .exe is locked and may be an MCP server the host is actively using.

- Build to an alternate target dir (`CARGO_TARGET_DIR=...`).
- Stage the new binary next to the old one (`programmer.exe.new`).
- Rename-swap only when the process is stopped - and if the process is an MCP
  server, the USER restarts it at their boundary, not the AI mid-session.

## kill_process hygiene

Before `kill_process`, run `server_health` and `list_process` - confirm the
target is not a live MCP server or something the user is working in. Prefer
letting owners stop their own processes.

## Deploys

`deploy_preflight` validates the selected project directory, its `src` folder,
and its Cargo manifest before you copy anything. Run `server_health` separately
when the operation also depends on a named process already running.

## Escalation

If a command is blocked or warned, do not shell-escape around the guard
(alternate encodings, indirection through scripts). Either the command is safe
enough to fix properly, or it should not run.
