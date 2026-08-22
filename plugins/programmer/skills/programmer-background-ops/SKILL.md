---
name: programmer-background-ops
description: Long-running work with Programmer - state-carrying shell sessions, live REPL shells, and WSL background jobs. Surface when a task runs longer than one tool call, needs state to persist across calls, or spans Windows and WSL. Watches, webhooks, and log tailing left this server in the v2.0 rebuild; this skill says where they went.
---

# Programmer Background Ops

## Sessions that keep state

Two tools, one distinction: `shell_session` remembers cwd and environment and
applies them to each fresh command; `live_shell` is a real long-lived process
holding a REPL with in-memory variables. Both take an `action` argument rather
than separate per-verb tools.

```
shell_session  action=create              (PowerShell or WSL flavor)
shell_session  action=run    "cmd"        (repeat; cwd and env persist)
shell_session  action=read                (recent output)
shell_session  action=cd | env | history
shell_session  action=destroy             (always clean up)
```

Use `shell_session` for multi-step builds and anything where `cd` or an env var
must stick. Use `live_shell` when the process itself must stay alive - a REPL,
an interactive prompt, or incremental reads from one running shell. The
`programmer-sessions` skill carries the full decision rule.

## WSL background jobs

```
wsl_bg "./long_pipeline.sh"   -> returns job_id
wsl_status job_id             (or job_id=all)
wsl_log job_id                (full or partial log)
```

One-shot Linux commands: `wsl_run` (returns summary + log path).

## What is no longer here

The v2.0 rebuild moved event-driven work off the dev shell. Do not reach for
these on `programmer` - they are not in its tool list:

| Need | Server | Tool |
|---|---|---|
| React to file changes | autonomous | `pulse_watch` |
| Receive an HTTP callback | autonomous | `pulse_webhook` |
| Desktop notification | local | `notify` |
| Page scraping | hands | `browser_http_scrape` |

Delta log polling did not disappear, it moved inside `read_file`: pass `tail=N`
for the last N lines, then feed the returned `since_bytes` back on the next call
to read only what was appended. For WSL jobs, poll `wsl_log` instead.

## Choosing the shape

| Situation | Tool |
|---|---|
| State must persist across calls | `shell_session` |
| Interactive REPL, variables in memory | `live_shell` |
| Long Linux job, poll later | `wsl_bg` + `wsl_log` |
| React to file changes | autonomous `pulse_watch` |
| Receive an HTTP callback | autonomous `pulse_webhook` |
