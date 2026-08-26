# Runtime verification

Release readiness requires evidence at five separate layers:

1. The expected release asset hash and Authenticode signature pass.
2. The host config contains the intended command and no unrelated changes.
3. MCP `initialize` returns the expected server name and version.
4. `tools/list` returns the documented tool count for the release under test
   (`v2.0.0-rc.1`: 49 tools in 10 ability groups).
5. Uninstall removes only Programmer and preserves every pre-existing config
   entry and every backup.

Run the repo-contained read-only protocol probe against an extracted
executable:

```powershell
.\distribution\Test-ProgrammerMcp.ps1 `
    -ProgrammerPath '.\path\to\programmer.exe' `
    -ExpectedName 'programmer' `
    -ExpectedVersion '2.0.0-rc.1'
```

For both signed release-candidate portable artifacts, the accepted result is:

- `ToolCount`: 49
- `CategoryCount`: 10
- `ToolContractMatches`: true
- `ServerName`: `programmer`
- `ServerVersion`: `2.0.0-rc.1`
- `IdentityMatches`: true

The same acceptance must be rerun against the exact bytes under review; a source
test or different artifact is not a substitute.

For clean install and uninstall testing, use a separate Windows account or VM.
The RC honors explicit `APPDATA` and `USERPROFILE` roots, which supports a bounded
compatibility harness, but that does not replace a real clean-host acceptance run.
Snapshot the host config before install, after install, and after uninstall;
compare parsed JSON semantics as well as raw hashes. Run two installs in the same
second and preserve both backups before uninstall.
