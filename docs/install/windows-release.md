# Windows release selection and verification

Use the fixed `v0.2.0-alpha` release page, not an unpinned "latest" URL:

<https://github.com/AIWander/Programmer-Wander/releases/tag/v0.2.0-alpha>

## Published assets

| Asset | SHA-256 |
| --- | --- |
| `Programmer-Wander-Setup-arm64.exe` | `f8191664702ff756c7b494c9a32ea8e45efb4c6d11734da40affed4cc8260936` |
| `Programmer-Wander-Setup-x64-server-only.exe` | `2ad4a1c0e81a860f9259bbfd17f3875303555ef7bf69b0f95735ab0c25dafed1` |
| `Programmer-Wander-Setup-x64.exe` | `cfe704e436429390eece84aa81353ed447cefebf35de7e57e6eec515f32c9e0e` |
| `programmer-wander-windows-arm64.zip` | `8e7eed3369a1974a56c9e1a0d6978fdc9e98fa5ccf9a5a1efc02059833124dd4` |
| `programmer-wander-windows-x64.zip` | `9ccbaec21cead989da4dd82f4fc861e84104a13c1024c0e62496273838ab3ad8` |

The values above were re-read from the release API and the published
`SHA256SUMS` on 2026-07-23. Recheck the release page before relying on them
later.

## Verify a download

Run this from the directory containing the downloaded asset:

```powershell
$Asset = Resolve-Path -LiteralPath '.\programmer-wander-windows-x64.zip'
$ExpectedSha256 = '9ccbaec21cead989da4dd82f4fc861e84104a13c1024c0e62496273838ab3ad8'
$ActualSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Asset).Hash.ToLowerInvariant()
if ($ActualSha256 -ne $ExpectedSha256) {
    throw "SHA-256 mismatch: $ActualSha256"
}
```

For an installer or extracted executable, also inspect Authenticode:

```powershell
$Signature = Get-AuthenticodeSignature -LiteralPath $Asset
$Signature | Select-Object Status, StatusMessage, SignerCertificate
if ($Signature.Status -ne 'Valid') {
    throw "Authenticode validation failed: $($Signature.Status)"
}
```

Hash and signature validation prove artifact integrity and signer status. They
do not prove correct runtime identity, safe backup behavior, host discovery, or
uninstall semantics.

## Current alpha limits

- Fresh x64 and ARM64 artifact probes returned MCP server identity
  `antigravity-rs` `1.0.0` instead of Programmer `0.2.0-alpha`.
- The config backup name has one-second resolution, so rapid install/uninstall
  operations can overwrite a backup.
- Changing `USERPROFILE` is not a valid isolation strategy for clean testing.
  Use a separate Windows account or VM.

Do not automate public installation or call this release one-click ready until
those defects are fixed and the replacement artifacts pass the verification
guide.
