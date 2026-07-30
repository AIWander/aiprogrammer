# Runtime verification

Release readiness requires evidence at five separate layers:

1. The expected release asset hash and Authenticode signature pass.
2. The host config contains the intended command and no unrelated changes.
3. MCP `initialize` returns the expected server name and version.
4. `tools/list` returns 105 tools in the 11 documented categories.
5. Uninstall removes only Programmer and preserves every pre-existing config
   entry and every backup.

Run the repo-contained read-only protocol probe against an extracted
executable:

```powershell
.\distribution\Test-ProgrammerMcp.ps1 `
    -ProgrammerPath '.\path\to\programmer.exe' `
    -ExpectedName 'programmer-wander' `
    -ExpectedVersion '0.2.0-alpha'
```

For both current published portable artifacts, the observed result is:

- `ToolCount`: 105
- `CategoryCount`: 11
- `ToolContractMatches`: true
- `ServerName`: `antigravity-rs`
- `ServerVersion`: `1.0.0`
- `IdentityMatches`: false

That is a stop-ship failure, not a cosmetic warning.

For clean install and uninstall testing, use a separate Windows account or VM.
The current executable's home-directory lookup is not isolated by changing
`USERPROFILE`. Snapshot the host config before install, after install, and
after uninstall; compare parsed JSON semantics as well as raw hashes. Run a
rapid install/uninstall scenario specifically to prove backup filenames cannot
collide.
