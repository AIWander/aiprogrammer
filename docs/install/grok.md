# Grok CLI

Status: manual configuration prepared; not a native RC installer target.

## 1. Install and verify the server

Follow [Windows release selection and verification](windows-release.md). For a
portable extraction, open PowerShell in the extracted directory:

```powershell
$ProgrammerExe = (Resolve-Path -LiteralPath '.\programmer.exe').Path
& $ProgrammerExe --version
```

## 2. Register the MCP server

Back up `~/.grok/config.toml` before editing it:

```powershell
$GrokConfig = Join-Path $env:USERPROFILE '.grok\config.toml'
if (Test-Path -LiteralPath $GrokConfig) {
    Copy-Item -LiteralPath $GrokConfig -Destination "$GrokConfig.pre_programmer_$(Get-Date -Format 'yyyyMMdd_HHmmss_fffffff').bak"
}
```

Then add one `programmer` STDIO entry, using your real extracted path:

```toml
[mcp_servers.programmer]
command = "C:\\path\\to\\programmer.exe"
args = []
```

The v2.0.0-rc.1 CLI does not list a Grok target, so use the reviewed manual entry.
Reload MCP servers (press `r` in `/mcps`) or start a fresh Grok session, then
confirm the programmer tools appear.

## 3. Install one plugin profile

Grok CLI reads the same marketplace format as Claude Code. Either add the
repository as a marketplace source in `~/.grok/config.toml`:

```toml
[[marketplace.sources]]
name = "aiprogrammer"
path = "C:\\path\\to\\cloned\\aiprogrammer"
```

or install the plugin directory directly from a local clone:

```powershell
grok plugin install "C:\path\to\cloned\aiprogrammer\plugins\programmer-skills"
```

Review the plugin before accepting Grok's trust prompt. Install exactly one
profile: `programmer-skills` (skills only), or `programmer` if you want the
inert hook templates present for separate review. Installing the plugin does
not activate hooks and does not define an MCP server, so it cannot double-spawn
the entry you registered in step 2.

## 4. Optional guard hooks

Read `plugins/programmer/hooks/opt-in/README.md`, run
`plugins/programmer/scripts/render-hooks.ps1`, and review
`rendered-hooks/grok-hooks.json`. Merge only the entries you want into your
Grok hooks configuration yourself, then prove the hook fires with a harmless
event before treating it as enforcement.

## 5. Restart and verify

Start a fresh Grok session and verify with the
[runtime verification guide](verify.md): MCP `initialize` and `tools/list`
must both match the release.
