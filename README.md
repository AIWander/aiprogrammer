# AIProgrammer

> Skills, guard hooks, and plugin profiles for the free
> [Programmer-Wander](https://github.com/AIWander/Programmer-Wander) MCP server -
> the dev shell that gives any AI a complete Rust + Windows toolbox.

**Site:** [aiprogrammer.ai](https://aiprogrammer.ai)

Programmer-Wander is a single signed binary exposing a Rust + Windows dev shell.
The v2.0 surface is 49 tools in 10 organized categories (Files, Shell, Sessions,
Search, System, WSL, Transforms + Stats, Net, Guard, Infra + Meta). This repository
is the plugin kit that teaches an AI host how to use it well - and, optionally,
how to guard it.

## Install status

The current server release is the signed portable `v2.0.0-rc.1` release candidate.
Its x64 and ARM64 binaries report `programmer` `2.0.0-rc.1`, expose exactly 49
unique tools, honor explicit profile roots, create collision-proof backups, and
pass isolated-profile install/runtime/uninstall checks. The ARM64 binary was tested
natively; x64 was compatibility-tested on the ARM64 Windows host, so native-x64
hardware acceptance and the ten-person cold-test gate remain open. This RC does not
claim a one-click MSI installer or production-stable status.

See the [host install guides](docs/install/README.md) for the exact supported
paths, release hashes, verification steps, and blocked channels.

## Install

1. Download the correct signed portable zip from the exact
   [`v2.0.0-rc.1` release](https://github.com/AIWander/Programmer-Wander/releases/tag/v2.0.0-rc.1)
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
| `programmer-background-ops` | Persistent shells, WSL jobs, and alternatives for removed watcher/webhook tools |
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

## Optional voice add-on

Programmer works on its own. For local hands-free headset use, add the separate
free [Voice-Command v3.0.0](https://github.com/AIWander/Voice-Command/releases/tag/v3.0.0).
Voice requires microphone permission and its own setup. Web or mobile AI access
also requires an authenticated remote connector back to the Windows host.

## Upgrade

Programmer is free and stays free. The future upgrade is **UniMan** - a universal
manager that delegates work to Claude Code, Codex CLI, and Grok Build CLI, with
one live dashboard covering both products (it detects your Programmer install
automatically). Manager is beta/coming soon; there is no published checkout or
price. Details at [aiprogrammer.ai](https://aiprogrammer.ai).

## License

Apache 2.0. See [LICENSE](LICENSE).
