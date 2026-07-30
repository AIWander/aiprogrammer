# Codex

Status: STAGED for controlled testing; not READY for public submission.

Programmer-Wander has no `install --target codex` target in `v0.2.0-alpha`.
Use Codex's own MCP command after verifying the executable.

## 1. Register the MCP server

Open PowerShell in the portable extraction directory:

```powershell
$ProgrammerExe = (Resolve-Path -LiteralPath '.\programmer.exe').Path
& $ProgrammerExe --version
codex mcp add programmer -- $ProgrammerExe
codex mcp get programmer --json
```

`codex mcp add` writes user configuration. Back up the existing Codex config
independently before running it:

```powershell
$CodexConfig = Join-Path $env:USERPROFILE '.codex\config.toml'
if (Test-Path -LiteralPath $CodexConfig) {
    $Backup = "$CodexConfig.pre_programmer_$(Get-Date -Format 'yyyyMMdd_HHmmss_fffffff').bak"
    Copy-Item -LiteralPath $CodexConfig -Destination $Backup
    if ((Get-FileHash $CodexConfig).Hash -ne (Get-FileHash $Backup).Hash) {
        throw 'Codex config backup verification failed.'
    }
}
```

## 2. Install one plugin profile

```powershell
codex plugin marketplace add AIWander/aiprogrammer
codex plugin add programmer-skills@aiprogrammer
```

Use `programmer@aiprogrammer` instead only if you want the inert hook templates
available for explicit review. Plugin installation does not trust or activate
hook definitions automatically.

## 3. Restart and verify

Restart Codex, open a new task, and verify both the plugin and MCP connection.
The current alpha still fails the expected Programmer identity check described
in [runtime verification](verify.md), so do not treat discovery as release
readiness.
