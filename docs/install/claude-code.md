# Claude Code

Status: STAGED for controlled testing; not READY for public submission.

## 1. Install and verify the server

Follow [Windows release selection and verification](windows-release.md). For a
portable extraction, open PowerShell in the extracted directory:

```powershell
$ProgrammerExe = (Resolve-Path -LiteralPath '.\programmer.exe').Path
& $ProgrammerExe --version
```

Before allowing the alpha installer to edit Claude Code configuration, make an
independent backup with sub-second uniqueness:

```powershell
$ClaudeSettings = Join-Path $env:USERPROFILE '.claude\settings.json'
if (Test-Path -LiteralPath $ClaudeSettings) {
    $Backup = "$ClaudeSettings.pre_programmer_$(Get-Date -Format 'yyyyMMdd_HHmmss_fffffff').bak"
    Copy-Item -LiteralPath $ClaudeSettings -Destination $Backup
    if ((Get-FileHash $ClaudeSettings).Hash -ne (Get-FileHash $Backup).Hash) {
        throw 'Claude Code config backup verification failed.'
    }
}
```

Register the server only after reviewing that backup:

```powershell
& $ProgrammerExe install --target claude-code
```

Do not script an immediate uninstall after install. The current release can
reuse a second-resolution backup filename.

## 2. Install one plugin profile

```powershell
claude plugin marketplace add AIWander/aiprogrammer
claude plugin install programmer-skills@aiprogrammer
```

Use `programmer@aiprogrammer` instead only if you want the inert hook templates
present for separate review. Installing the plugin does not activate those
hooks.

## 3. Restart and verify

Restart Claude Code, then verify the installed plugin and MCP tools in a new
session. Use the [runtime verification guide](verify.md). A visible plugin,
running process, or successful `--version` call is not enough: MCP
`initialize` and `tools/list` must both match the release.

Clean-host acceptance must use a separate Windows account or VM. Overriding
`USERPROFILE` alone does not redirect the current binary's home lookup.
