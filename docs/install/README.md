# Install guides

Programmer-Wander `v2.0.0-rc.1` is a signed portable Windows release candidate.
The public ZIP route is available; one-click installer, native-x64 hardware, and
ten-person cold-test gates remain open.

| Host or channel | Current state | What is available |
| --- | --- | --- |
| Claude Code | RC AVAILABLE | Signed portable executable plus documented CLI registration and plugin profiles |
| Codex | RC AVAILABLE | Signed portable executable plus documented `codex mcp` registration and plugin metadata |
| Claude Desktop | RC AVAILABLE | Signed portable executable with `install --target claude-desktop` |
| LM Studio | RC AVAILABLE | Signed portable executable with `install --target lm-studio` and config guide |
| Cowork | NOT ADVERTISED | The RC CLI has no `cowork` install target |
| WinGet | BLOCKED | No ratified package identifier and current release defects remain |
| Official MCP Registry | BLOCKED | No public MCPB URL or ratified registry identity |
| Anthropic official marketplace | BLOCKED | Submission is approval-gated and clean-host/runtime gates are open |
| OpenAI Plugins Directory | BLOCKED | Skills-only submission materials, legal URLs, identity, and review tests are incomplete |

`RC AVAILABLE` means the signed portable artifact and local acceptance evidence
exist. It does not mean a public directory submission, native-x64 hardware pass,
or ten-person clean-machine gate has passed. `BLOCKED` means a named prerequisite
is missing.

Start here:

- [Windows release selection and hash verification](windows-release.md)
- [Claude Code](claude-code.md)
- [Codex](codex.md)
- [Claude Desktop](claude-desktop.md)
- [LM Studio](lm-studio.md)
- [Runtime verification](verify.md)

The plugin profiles are separate from the MCP server:

- `programmer`: six skills plus inert, reviewable hook templates.
- `programmer-skills`: the same six skills with no hook code.

Install exactly one profile. Neither profile installs the executable or edits a
host's MCP configuration.
