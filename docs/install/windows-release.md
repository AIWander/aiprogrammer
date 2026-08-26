# Windows release selection and verification

Use the fixed `v2.0.0-rc.1` prerelease page, not an unpinned "latest" URL:

<https://github.com/AIWander/Programmer-Wander/releases/tag/v2.0.0-rc.1>

## Published assets

| Asset | SHA-256 |
| --- | --- |
| `programmer-wander-v2.0.0-rc.1-windows-arm64.zip` | `828623feec9072e761af7b4cefcfe73ffe3f2c8ff48809c7f4882cb608af6887` |
| `programmer-wander-v2.0.0-rc.1-windows-x64.zip` | `2856d68a1bb92dff34db70a958a00cb82f093793126e13f8ac6a1fdcbd942eeb` |

The values above are bound to the release-candidate package build and must match
the published `SHA256SUMS` on the release. Recheck the release page before relying
on them later.

## Verify a download

Run this from the directory containing the downloaded asset:

```powershell
$Asset = Resolve-Path -LiteralPath '.\programmer-wander-v2.0.0-rc.1-windows-x64.zip'
$ExpectedSha256 = '2856d68a1bb92dff34db70a958a00cb82f093793126e13f8ac6a1fdcbd942eeb'
$ActualSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Asset).Hash.ToLowerInvariant()
if ($ActualSha256 -ne $ExpectedSha256) {
    throw "SHA-256 mismatch: $ActualSha256"
}
```

Extract the ZIP, then inspect Authenticode on the executable:

```powershell
$Programmer = Resolve-Path -LiteralPath '.\programmer-v2-rc\programmer.exe'
$Signature = Get-AuthenticodeSignature -LiteralPath $Programmer
$Signature | Select-Object Status, StatusMessage, SignerCertificate
if ($Signature.Status -ne 'Valid') {
    throw "Authenticode validation failed: $($Signature.Status)"
}
```

Hash and signature validation prove artifact integrity and signer status. They
do not prove correct runtime identity, safe backup behavior, host discovery, or
uninstall semantics.

The accepted signed executable hashes are:

| Architecture | Extracted `programmer.exe` SHA-256 |
| --- | --- |
| ARM64 | `8ff2c0031bd6de201687a6397f09c7d6709afce7114ff6eef8bf581327737259` |
| x64 | `df5036945b2e9665a4fdb3c15ba6a9b20b06a5460b16f01468bf8d0641bb50d0` |

Require signature status `Valid`, signer subject beginning `CN=Joseph Wander`, and
a timestamp certificate.

## Current RC limits

- This RC ships signed portable ZIPs, not a one-click MSI.
- ARM64 ran natively on the build host. x64 passed Windows compatibility execution
  on that ARM64 host; native-x64 hardware proof remains open.
- Explicit `APPDATA` and `USERPROFILE` roots, collision-proof backups, install,
  initialize, 49-tool discovery, safe/block behavior, and uninstall passed in an
  isolated profile. A real separate Windows account or VM is still required for
  the public cold-test gate.
- The 8-of-10 no-rescue cold-test gate has not run, so no public success percentage
  is claimed.

Do not call this RC production-stable or one-click ready. Preserve the exact tag,
asset hash, and architecture in support reports.
