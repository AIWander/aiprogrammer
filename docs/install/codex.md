# Codex

Status: signed portable RC available; directory submission remains separate.

Programmer-Wander has no `install --target codex` target in `v2.0.0-rc.1`.
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
The accepted RC result is server name `programmer`, version `2.0.0-rc.1`, and
exactly 49 unique tools. Discovery alone is not that proof.
