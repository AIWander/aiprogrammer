# AIProgrammer

> Skills, guard hooks, and plugin profiles for the free
> [Programmer-Wander](https://github.com/AIWander/Programmer-Wander) MCP server -
> the dev shell that gives any AI a complete Rust + Windows toolbox.

**Site:** [aiprogrammer.ai](https://aiprogrammer.ai)

Programmer-Wander is a single signed binary exposing a Rust + Windows dev shell.
The v2.0 surface is 49 tools in 10 organized categories (Files, Shell, Sessions,
Search, System, WSL, Transforms + Stats, Net, Guard, Infra + Meta); the earlier
`v0.2.0-alpha` release exposed 105 tools in 11 categories. This repository is the
plugin kit that teaches an AI host how to use it well - and, optionally, how to
guard it.

## Install status

The current server release, `v0.2.0-alpha`, is for controlled Windows alpha
testing. It is not yet a broad one-click release. A fresh probe of the published
x64 and ARM64 portable artifacts found three release blockers:

- `programmer.exe --version` reports `0.2.0-alpha`, but MCP `initialize`
  identifies the server as `antigravity-rs` version `1.0.0`.
- install and uninstall operations started within the same second can reuse a
  backup filename and overwrite the earlier host-config backup.
- overriding `USERPROFILE` does not isolate the executable's home-directory
  lookup, so a separate Windows account or VM is required for clean-host proof.

The server still returned the documented 105 tools in 11 categories, but that
does not clear the identity, backup-integrity, or clean-host defects.

See the [host install guides](docs/install/README.md) for the exact supported
paths, release hashes, verification steps, and blocked channels.

## Install

1. Download the correct signed installer or portable zip from the
   [`v0.2.0-alpha` release](https://github.com/AIWander/Programmer-Wander/releases/tag/v0.2.0-alpha)
   and verify it against the published `SHA256SUMS`.
2. Follow the guide for
   [Claude Code](docs/install/claude-code.md),
   [Codex](docs/install/codex.md),
   [Grok CLI](docs/install/grok.md),
   [Claude Desktop](docs/install/claude-desktop.md), or
   [LM Studio](docs/install/lm-studio.md).
3. Add this repository through the host's plugin flow, then install exactly ONE
   profile:

| Profile | Contents |
| --- | --- |
| `programmer` | Six skills plus inert, reviewable guard-hook templates |
| `programmer-skills` | The same six skills with no hook code |

The plugin profiles teach a host how to use an existing `programmer` MCP
connection. They do not install the server or silently activate hooks.

## The six skills

| Skill | Job |
|-------|-----|
| `programmer-getting-started` | Orientation: category map, first moves, hard-won rules |
| `programmer-toolmap` | Full per-tool reference, organized by category |
| `programmer-dev-loop` | The edit-build-test-commit loop, cargo-on-Windows rules |
| `programmer-background-ops` | Persistent shells, WSL jobs, watchers, webhooks, delta polling |
| `programmer-safe-ops` | Command pre-flight, archive-first, staged swaps, kill hygiene |
| `programmer-sessions` | Choosing between shell_session and live_shell, and their recovery semantics |

## The guard hooks (opt-in, never auto-loaded)

The `programmer` profile ships hook templates that stay inert until you review
and render them: the policy denies destructive delete patterns, bare
force-pushes, and kills aimed at running MCP servers; warns on cargo via
PowerShell and writes into protected config roots; and audits every decision
locally. Read `plugins/programmer/hooks/opt-in/README.md`, then run
`plugins/programmer/scripts/render-hooks.ps1` and merge only what you want.
Rendering writes host-ready JSON with your real paths into
`plugins/programmer/rendered-hooks/` (local only, not tracked); Claude-style,
Grok, and Codex fragments all share the one reviewed policy file.

## Upgrade

Programmer is free and stays free. The $5 upgrade is **UniMan** - a universal
manager that delegates work to Claude Code, Codex CLI, and Grok Build CLI, with
one live dashboard covering both products (it detects your Programmer install
automatically). Details at [aiprogrammer.ai](https://aiprogrammer.ai).

## License

Apache 2.0. See [LICENSE](LICENSE).
