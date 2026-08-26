---
name: programmer-toolmap
description: Full organized reference for all Programmer tools by category - Files, Shell, Sessions, Search, System, WSL, Transforms, Net, Guard, Meta. Surface when choosing which programmer tool fits a task, when a tool call failed and an alternative is needed, or when the user asks what programmer can do.
---

# Programmer Toolmap (v2.0 surface - 49 tools)

Every tool, grouped as the server presents them. The 2026-07-29 rebuild retired the legacy
alias layer and name-duplicates, merged mode-variants, and moved non-dev-shell capabilities
to their proper homes (git -> the gitplus add-on server; watches/webhooks -> autonomous;
scraping -> hands). What remains is the dev shell.

## [Files] (7)

| Tool | Use |
|---|---|
| `read_file` | One reader, four modes: plain read (auto-truncates), `search=` pattern grep, `range=` line span (e.g. 50:100), `tail=` last N lines - pass `since_bytes` from a previous tail for delta polling of growing logs |
| `write_file` | Write/overwrite (creates parent dirs); `mode=append` streams to the end. NOT for surgical edits |
| `edit_block` | Guarded code surgery: exact literal match, fails unless the occurrence count equals `expected_replacements` |
| `copy_file` / `move_file` | Copy with metadata / move or rename |
| `create_dir` / `list_dir` | Make dirs / list contents recursively |

## [Shell] (5)

| Tool | Use |
|---|---|
| `cmd` | One-off command through `cmd.exe /C`, output + exit code |
| `powershell` | One-off PowerShell - the versatile Windows tool (never for cargo; use cmd) |
| `shortcut` | `mode=list` saved shortcuts; `mode=run` executes `names=[]` (saved, `$param` substitution via `params`) and/or `commands=[]` (raw sequence), inside `session_id`, `stop_on_error` control |
| `list_process` / `kill_process` | Process listing / kill by PID |

## [Sessions] (2) - see the programmer-sessions skill for the decision rule

| Tool | Use |
|---|---|
| `shell_session` | Remembered cwd + env applied to each fresh command. Actions: create, run, list, destroy, cd, env, history, read. Auto-persists; survives restarts with no ceremony |
| `live_shell` | Real long-lived PowerShell/WSL process: REPLs, in-memory variables, incremental reads. Actions: create, run, read, history, list, destroy, checkpoint, recover |

## [Search] (1)

| Tool | Use |
|---|---|
| `search_file` | Find files by name or content |

## [System] (5)

| Tool | Use |
|---|---|
| `screenshot` | Troubleshooting screenshot -> file path only, 1MB cap |
| `system_info` | OS, CPU, memory |
| `clipboard_read` / `clipboard_write` | Clipboard I/O |
| `md2docx` | Markdown -> DOCX (needs pandoc) |

## [WSL] (4)

| Tool | Use |
|---|---|
| `wsl_run` | Run in WSL, summary + log path |
| `wsl_bg` / `wsl_status` / `wsl_log` | Background job: launch / poll / read log |

## [Transforms + Stats] (14)

| Tool | Use |
|---|---|
| `base64` | `mode=encode` or `decode` |
| `json` | `mode=format` or `minify` |
| `convert` | Tabular: `from=csv,to=json` or `from=json,to=csv` |
| `grep` | Regex search with context across file(s) |
| `file_stats` | Node metadata (size, timestamps, readonly) + recursive dir aggregation (counts, total size) |
| `diff_file` | Unified diff of two files |
| `transform_find_replace` | Bulk find/replace: multi-file, regex, NO count guard (contrast edit_block) |
| `transform_hash_file` | MD5/SHA256 checksum |
| `transform_bulk_rename` | Regex batch rename (dry_run default) |
| `transform_sync_dir` | Dir sync: mirror/update/backup (dry_run default) |
| `transform_file` | Python expression over matching files (needs python) |
| `transform_scaffold` | Project boilerplate: rust-mcp, python-mcp, nextjs, fastapi, expo |
| `archive_create` / `archive_extract` | zip/tar create and extract |

## [Net] (2)

| Tool | Use |
|---|---|
| `http_request` | HTTP call; `save=` downloads body to disk with Range-resume |
| `port_check` | Is this host:port open |

## [Guard] (2)

| Tool | Use |
|---|---|
| `security_check_cmd` | Screen a command for dangerous patterns before running it |
| `security_audit_log` | Recent security audit entries |

## [Infra + Meta] (7)

| Tool | Use |
|---|---|
| `server_health` | Which MCP servers are alive |
| `deploy_preflight` | Pre-deploy checks for a server target |
| `config_validate_mcp` | Validate an MCP config file |
| `plan` | Task ingredient analysis; `assemble=` enriches an existing plan |
| `sqlite_query` | Read-only SELECT against a .db |
| `registry_read` | Windows registry read (approved roots) |
| `doctor` | Per-host capability self-report: git, WSL distros, shells, python/pandoc/cargo, profile |

## What moved where (so you look in the right server)

- Git (all of it, plus GitHub/GitLab/Gitea APIs) -> the **gitplus** add-on server; or shell out via `cmd`.
- Resource watches + inbound webhooks -> **autonomous** (`pulse_watch`, `pulse_webhook`).
- Page scraping -> **hands** (`browser_http_scrape`); desktop notifications -> **local** (`notify`).
- All supported builds expose the same 49-tool contract; feature flags do not add another public tool.
