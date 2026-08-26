# Claude Desktop

Status: signed portable RC available; MCPB packaging remains unaccepted.

Two local paths exist:

1. Register a verified portable executable with:

   ```powershell
   $ProgrammerExe = (Resolve-Path -LiteralPath '.\programmer.exe').Path
   & $ProgrammerExe install --target claude-desktop
   ```

2. Build and inspect an architecture-specific MCPB candidate from
   [`distribution/mcpb`](../../distribution/mcpb/README.md).

Before the CLI edits Claude Desktop configuration, independently back up the
existing file with sub-second uniqueness:

```powershell
$ClaudeConfig = Join-Path $env:APPDATA 'Claude\claude_desktop_config.json'
if (Test-Path -LiteralPath $ClaudeConfig) {
    $Backup = "$ClaudeConfig.pre_programmer_$(Get-Date -Format 'yyyyMMdd_HHmmss_fffffff').bak"
    Copy-Item -LiteralPath $ClaudeConfig -Destination $Backup
    if ((Get-FileHash $ClaudeConfig).Hash -ne (Get-FileHash $Backup).Hash) {
        throw 'Claude Desktop config backup verification failed.'
    }
}
```

Do not double-click or distribute the repo's older MCPB candidates as production
packages. They do not contain the accepted v2 RC bytes. The MCPB format also cannot express Windows CPU architecture
in its current compatibility object, so x64 and ARM64 are separate,
architecture-labelled files.

The RC CLI uses unique backup names even for repeated same-second operations.
Restart Claude Desktop after any approved configuration change, then run the
[runtime verification guide](verify.md).
