# Claude Code

Status: signed portable RC available; plugin-directory submission remains separate.

## 1. Install and verify the server

Follow [Windows release selection and verification](windows-release.md). For a
portable extraction, open PowerShell in the extracted directory:

```powershell
$ProgrammerExe = (Resolve-Path -LiteralPath '.\programmer.exe').Path
& $ProgrammerExe --version
```

Before allowing the RC CLI to edit Claude Code configuration, make an independent
backup as an additional recovery layer:

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

The RC also creates a unique recoverable backup on every config write, including
multiple operations in the same second.

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

The RC honors explicit `USERPROFILE` and `APPDATA` roots. The public cold-test gate
still requires a separate Windows account or VM rather than treating an environment
override as complete clean-machine proof.
