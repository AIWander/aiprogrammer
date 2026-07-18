# AIProgrammer

> Skills, guard hooks, and plugin profiles for the free
> [Programmer-Wander](https://github.com/AIWander/Programmer-Wander) MCP server -
> the dev shell that gives any AI a complete Rust + Windows toolbox.

**Site:** [aiprogrammer.ai](https://aiprogrammer.ai)

Programmer-Wander is a single signed binary exposing 105 tools in 11 organized
categories (Files, Search, Shell, Git, Sessions, Background, Net, Data, System,
Guard, Plan). This repository is the plugin kit that teaches an AI host how to
use it well - and, optionally, how to guard it.

## Install

1. Install the server: download the signed installer or portable zip from
   [Programmer-Wander releases](https://github.com/AIWander/Programmer-Wander/releases)
   and register it (`programmer.exe install --target <host>`).
2. Add this repository through your host's plugin flow (for Claude Code:
   `claude plugin marketplace add AIWander/aiprogrammer`), then install exactly
   ONE profile:

| Profile | Contents |
| --- | --- |
| `programmer` | Five skills plus inert, reviewable guard-hook templates |
| `programmer-skills` | The same five skills with no hook code |

## The five skills

| Skill | Job |
|-------|-----|
| `programmer-getting-started` | Orientation: category map, first moves, hard-won rules |
| `programmer-toolmap` | Full per-tool reference, organized by category |
| `programmer-dev-loop` | The edit-build-test-commit loop, cargo-on-Windows rules |
| `programmer-background-ops` | Persistent shells, WSL jobs, watchers, webhooks, delta polling |
| `programmer-safe-ops` | Command pre-flight, archive-first, staged swaps, kill hygiene |

## The guard hooks (opt-in, never auto-loaded)

The `programmer` profile ships hook templates that stay inert until you review
and render them: the policy denies destructive delete patterns, bare
force-pushes, and kills aimed at running MCP servers; warns on cargo via
PowerShell and writes into protected config roots; and audits every decision
locally. Read `plugins/programmer/hooks/opt-in/README.md`, then run
`plugins/programmer/scripts/render-hooks.ps1` and merge only what you want.
Files in `plugins/programmer/rendered-hooks/` are examples - re-render for your
own paths.

## Upgrade

Programmer is free and stays free. The $5 upgrade is **UniMan** - a universal
manager that delegates work to Claude Code, Codex CLI, and Grok Build CLI, with
one live dashboard covering both products (it detects your Programmer install
automatically). Details at [aiprogrammer.ai](https://aiprogrammer.ai).

## License

Apache 2.0. See [LICENSE](LICENSE).
