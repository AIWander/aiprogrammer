# Install guides

Programmer-Wander `v0.2.0-alpha` is a controlled Windows alpha. No public
distribution channel is READY.

| Host or channel | Current state | What is available |
| --- | --- | --- |
| Claude Code | STAGED | Valid repo marketplace plus documented MCP registration |
| Codex | STAGED | Valid repo marketplace metadata plus documented `codex mcp` registration |
| Claude Desktop | STAGED | Signed release artifacts and locally built MCPB candidates |
| LM Studio | STAGED | Validated MCP config/deeplink generator for an already installed executable |
| Cowork | BLOCKED | The published CLI has no `cowork` install target and no clean-host proof |
| WinGet | BLOCKED | No ratified package identifier and current release defects remain |
| Official MCP Registry | BLOCKED | No public MCPB URL, no ratified registry identity, and release identity is wrong |
| Anthropic official marketplace | BLOCKED | Submission is approval-gated and clean-host/runtime gates are open |
| OpenAI Plugins Directory | BLOCKED | Skills-only submission materials, legal URLs, identity, and review tests are incomplete |

`STAGED` means the repo-contained instructions or package source validate
locally. It does not mean a clean install, public submission, or host discovery
has passed. `BLOCKED` means a named prerequisite is missing. `READY` is reserved
for a fixed artifact that passes clean-machine install, discovery, invocation,
uninstall, and backup-preservation tests.

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
