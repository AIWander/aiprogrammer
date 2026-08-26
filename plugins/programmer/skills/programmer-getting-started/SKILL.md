---
name: programmer-getting-started
description: Orientation for the Programmer MCP server - a single-binary Rust + Windows dev shell with 49 tools in 10 categories (Files, Shell, Sessions, Search, System, WSL, Transforms + Stats, Net, Guard, Infra + Meta). Surface when programmer is registered in the host, when picking a tool for file I/O, shells, sessions, WSL, HTTP, or transforms, when choosing between programmer and an alternative MCP server, or when answering "how do I do X with programmer".
---

# Programmer - Getting Started

Programmer is **the dev shell on this Windows machine**: one static-linked
`programmer.exe`, no external dependencies, no other servers required. The v2.0
surface is 49 tools in 10 categories:

| Category | What lives there (7/5/2/1/5/4/14/2/2/7 tools) |
|---|---|
| Files | `read_file`, `write_file`, `edit_block`, `copy_file`, `move_file`, `create_dir`, `list_dir` |
| Shell | `cmd`, `powershell`, `shortcut`, `list_process`, `kill_process` |
| Sessions | `shell_session` (remembered cwd/env), `live_shell` (real REPL process) |
| Search | `search_file` |
| System | `screenshot`, `system_info`, `clipboard_read`, `clipboard_write`, `md2docx` |
| WSL | `wsl_run`, `wsl_bg`, `wsl_log`, `wsl_status` |
| Transforms + Stats | `grep`, `json`, `base64`, `convert`, `file_stats`, `diff_file`, archives, `transform_*` |
| Net | `http_request`, `port_check` |
| Guard | `security_check_cmd`, `security_audit_log` |
| Infra + Meta | `server_health`, `doctor`, `deploy_preflight`, `config_validate_mcp`, `plan`, `sqlite_query`, `registry_read` |

Full per-tool reference: see the `programmer-toolmap` skill.

The 2026-07-29 v2.0 rebuild retired the legacy alias layer and moved non-dev-shell
capabilities out: git to the gitplus add-on server, watchers and webhooks to
autonomous, scraping to hands. If you are driving the retired v0.2.0-alpha release
instead, it exposes a larger legacy surface whose descriptions carry `[Category]`
prefixes; check `tools/list` when the two disagree.

## Offload posture

Do mechanical work with programmer tool calls instead of reasoning it out
token-by-token: file I/O, shell commands, git, fetches, searches, transforms,
builds. Local compute does the I/O; the model's tokens do the reasoning.

## First moves

- One-off command: `cmd` (`cmd.exe /C`; use it for cargo and Git)
- Windows-specific cmdlets/ACLs/CIM: `powershell`
- Surgical code edit: `edit_block` (never `write_file` for edits)
- Long build: `shell_session` (action `create`, then `run`, then `read`)
- Interactive REPL that keeps variables in memory: `live_shell`
- Linux from Windows: `wsl_run`, or `wsl_bg` + `wsl_log` for long jobs

## When NOT to use programmer

| Need | Use instead |
|---|---|
| Browser/UI automation, OCR, vision | AI-Hands |
| Cross-session breadcrumbs / agent state | ops or autonomous |
| Knowledge base search / extraction | autonomous |
| Multi-AI delegation | manager / UniMan |
| Voice | Voice-Command |

## Hard-won rules

- cargo via `cmd`, never `powershell` - PowerShell pipes corrupt cargo output.
- `edit_block` over `write_file` for code surgery - atomic, context-preserving.
- A locked .exe cannot be overwritten while running: build to an alternate
  target dir, then swap with a rename. See `programmer-safe-ops`.

## Install / registration

`programmer.exe install --target claude-desktop|claude-code|lm-studio|cowork|all`
State directory `./.programmer/` sits next to the exe; fully portable.
Repo: https://github.com/AIWander/Programmer-Wander
