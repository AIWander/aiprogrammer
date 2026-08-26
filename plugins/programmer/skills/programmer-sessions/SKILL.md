---
name: programmer-sessions
description: Choosing between shell_session and live_shell - the one distinction in the rebuilt Programmer surface worth a decision rule. Fires when starting multi-command work, needing a REPL, needing state across commands, or recovering after a crash or restart.
---

# shell_session vs live_shell

Programmer has exactly two session mechanisms. They sound alike; they are different machines.
Pick on one axis: do you need a REMEMBERED CONTEXT, or a LIVING PROCESS?

## The decision rule

Use `shell_session` (default, cheap) when you need commands to share cwd and env vars:
build sequences, scripted steps, anything where each command can run in a FRESH process
as long as the working directory and environment carry over.

Use `live_shell` (heavier, holds an OS process open) when the value is IN the process:
an interactive REPL (python, node, sqlite), in-memory shell variables ($x = ...),
a long-running command you read incrementally, or WSL shell state.

If you are unsure, you almost always want `shell_session`. Reach for `live_shell`
only when a fresh-process-per-command model would lose something.

## What each one is

| | shell_session | live_shell |
|---|---|---|
| Mechanism | remembered state (cwd + env + history), fresh process per command | one long-lived PowerShell/WSL process you write to |
| Interactive REPL | no | yes |
| In-memory variables between calls | no (env vars yes, shell vars no) | yes |
| Incremental output from a running command | no | yes (action=read) |
| Cost | near zero | an open OS process |
| Crash recovery | AUTOMATIC - state persists to disk on every change; sessions reappear after a server restart | checkpoint/recover - see below |

## Recovery semantics (do not promise more than these)

- `shell_session` needs no ceremony: every change auto-persists under C:\CPC\state\shell_sessions;
  after a crash or restart the session is simply there again (cwd, env, history with output tails).
- `live_shell` cannot freeze a live process. `action=checkpoint` records what is sufficient to
  RECREATE an equivalent process: backend, cwd (probed live from the process when it responds),
  an env snapshot (stored for inspection - NOT auto-replayed), and command history.
  `action=recover` respawns the backend at the recorded cwd and restores history as context.
  In-memory variables are gone; the history tells you (or the model) what to replay by judgment.

## Common calls

```
shell_session(action=create, name=build, cwd=C:\my\project)
shell_session(action=env, session_id=build, key=RUST_LOG, value=debug)
shell_session(action=run, session_id=build, command=cargo test)
shell_session(action=read, session_id=build)          # recent output tails

live_shell(action=create, name=repl, shell=powershell)
live_shell(action=run, session_id=repl, command=$data = Import-Csv big.csv)
live_shell(action=run, session_id=repl, command=$data.Count)   # state survives
live_shell(action=checkpoint, session_id=repl)
live_shell(action=recover, session_id=repl)           # after a crash
```

## Anti-patterns

- Do not create a `live_shell` just to run three build commands - that is `shell_session` work.
- Do not expect `live_shell` recover to restore in-memory variables - re-derive them from history.
- Do not manage recovery files for `shell_session` by hand - persistence is automatic.
- One-off commands need neither: plain `cmd` or `powershell` is correct.
