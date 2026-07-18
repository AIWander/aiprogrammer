# Agent guide - AIWander/aiprogrammer

This repository is the CANONICAL home of the Programmer plugin kit (skills +
opt-in guard hooks + dual profiles). It was seeded 2026-07-18 from
Programmer-Wander's `plugins/` directory and is maintained going forward by the
assigned agent. The MCP server itself lives in
[AIWander/Programmer-Wander](https://github.com/AIWander/Programmer-Wander) -
server code changes happen THERE, plugin-kit changes happen HERE.

## Ground rules

- Apache-2.0, public repo. Nothing machine-specific or private lands here:
  no local absolute paths in docs (rendered-hooks/ examples are the one
  sanctioned exception and must say "re-render for your own paths"), no
  credentials, no internal infrastructure references.
- No emoji characters in any file in this repository.
- Hooks stay INERT: nothing in `hooks/opt-in/` may ever auto-load. The
  `__PLUGIN_ROOT__` token + `scripts/render-hooks.ps1` flow is the only
  activation path. A change that makes hooks self-activating is a regression.
- Install exactly one profile per host - keep `programmer` and
  `programmer-skills` skill-identical (same five skills, byte-for-byte) with
  hooks as the only difference.
- Skills describe the server's REAL tool contract. When Programmer-Wander's
  tools/list changes (count, categories, names), update `programmer-toolmap`
  and the counts in every skill + README in the same commit.

## Current state (as of seeding, 2026-07-18)

- Server: Programmer-Wander 0.2.0-alpha - 105 tools, 11 categories, every
  description prefixed `[Category]`, icon-embedded signed exe.
- Kit: five skills + guard-hook policy (tested 7/7 scenarios) + dual profiles
  + `.agents/plugins/marketplace.json`.
- Product model: Programmer free forever; UniMan is the $5 paid upgrade
  (universal manager + dashboard covering both). Upgrade copy currently links
  to aiprogrammer.ai / aiwander.ai - a real checkout URL does not exist yet.

## Backlog (in priority order)

1. De-duplicate the dual home: Programmer-Wander still contains a copy of
   `plugins/`. Replace that copy with a short pointer README to this repo (one
   PR there), so the kit has exactly one canonical source.
2. Landing page for aiprogrammer.ai (this repo can host it via GitHub Pages or
   a `site/` folder): free download + category tool map + the $5 UniMan
   upgrade card. Match the dark onboarding aesthetic shipped in the installer.
3. Swap the placeholder upgrade link for the real $5 checkout URL when the
   maintainer provides it (README here, Programmer-Wander README, and the
   installer onboarding page in the maintainer's build tree).
4. CI: a lint workflow that validates skill frontmatter, JSON files, the
   profile-parity rule (skills identical across profiles), and the no-emoji
   rule.
5. Track Programmer-Wander releases: on each server release, verify tool
   count/categories against a live tools/list and update skills accordingly.

## Verification habits

- After any hook-policy edit, re-run the scenario tests (pipe sample PreToolUse
  payloads through `hooks/opt-in/shared/policy/programmer_hook.py` and assert
  deny/warn/observe outcomes) before committing.
- After any skills edit, confirm both profiles remain identical:
  `diff -r plugins/programmer/skills plugins/programmer-skills/skills`.
