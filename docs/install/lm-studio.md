# LM Studio

Status: signed portable RC and manual config flow available; one-click deeplink remains separate.

LM Studio's `lmstudio://add_mcp` deeplink installs an MCP configuration. It does
not download or verify `programmer.exe`. Install and hash-check the executable
first.

## Generate a deeplink for an existing executable

Open PowerShell in this repository:

```powershell
$ProgrammerExe = (Resolve-Path -LiteralPath '.\path\to\programmer.exe').Path
.\distribution\lm-studio\New-LMStudioDeeplink.ps1 `
    -ProgrammerPath $ProgrammerExe `
    -ExpectedSha256 '<sha256-from-the-selected-release-asset>'
```

The generator:

- requires an existing absolute `.exe` path;
- optionally enforces an expected SHA-256;
- emits the exact MCP JSON entry;
- Base64-encodes only that entry, as LM Studio documents;
- URL-encodes the name and Base64 value;
- never opens the deeplink or edits LM Studio configuration.

Review the emitted JSON and link before opening it. The deeplink is configuration
only and must point to the exact verified v2 RC executable.

## Manual CLI registration

The published binary also exposes:

```powershell
& $ProgrammerExe install --target lm-studio
```

That command edits LM Studio's MCP configuration and creates a collision-proof
backup. An independent verified backup remains a useful defense before any config
change.

LM Studio follows Cursor-style `mcp.json` notation and supports local command
entries. See <https://lmstudio.ai/docs/app/mcp> and the official deeplink format
at <https://lmstudio.ai/docs/app/mcp/deeplink>.
