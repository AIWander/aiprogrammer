# programmer (plugin profile)

Full profile: six skills plus inert, reviewable guard-hook templates.

Contents:

- `skills/` - programmer-getting-started, programmer-toolmap,
  programmer-dev-loop, programmer-background-ops, programmer-safe-ops,
  programmer-sessions (each with an `agents/openai.yaml` Codex adapter)
- `hooks/opt-in/` - guard policy + Claude-style, Grok, and Codex adapters and
  fragments (never auto-loaded; see `hooks/opt-in/README.md`)
- `scripts/render-hooks.ps1` - renders fragments with this plugin's real path
  into `rendered-hooks/` (local only, not tracked)
- `instructions/APPLY_TO_YOUR_AI.txt` - per-client activation guidance

This profile expects an existing `programmer` MCP connection. It does not
install the server, edit host configuration, or wire hooks by itself - hook
wiring is an explicit, reviewed user step.

If you want skills only and no hook code at all, install the
`programmer-skills` profile instead. Install exactly one profile.
