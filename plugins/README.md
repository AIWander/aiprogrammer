# Plugins

Install exactly one current Programmer-Wander profile.

| Plugin | Purpose |
| --- | --- |
| `programmer` | Six skills plus inert guard-hook templates for hosts that can review, trust, and probe hooks |
| `programmer-skills` | The same six skills with no hook code |

Both profiles expect an existing `programmer` MCP connection (register the
server with `programmer.exe install --target <host>`, or by adding one STDIO
entry to the host's MCP configuration). Neither profile installs an MCP
endpoint, edits host configuration, swaps a binary, or restarts the server.
Hook wiring in the `programmer` profile is an explicit user step via
`scripts/render-hooks.ps1` after reviewing the policy source.

Host coverage: Claude Code and Grok CLI consume this marketplace format
directly; Codex reads the `.codex-plugin` manifests and the per-skill
`agents/openai.yaml` adapters; other MCP clients get the server plus the
pasteable guidance in each profile's `instructions/APPLY_TO_YOUR_AI.txt`.
The guard-hook fragments ship in Claude-style, Grok, and Codex variants that
all call the same reviewed policy file.
