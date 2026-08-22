$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$hooked = Join-Path $root 'plugins/programmer/skills'
$plain = Join-Path $root 'plugins/programmer-skills/skills'
$hookedSkills = @(Get-ChildItem -LiteralPath $hooked -Directory)
$plainSkills = @(Get-ChildItem -LiteralPath $plain -Directory)
# Census assertion, exact and intentional: bump this ONE constant when adding or removing a skill,
# and update the prose that quotes the count (plugin.json descriptions, README/AGENTS profile lines).
# Kept exact rather than "both profiles agree" so an accidental deletion still fails the build.
$expectedSkillCount = 6
if ($hookedSkills.Count -ne $expectedSkillCount -or $plainSkills.Count -ne $expectedSkillCount) {
    throw "Both profiles must contain exactly $expectedSkillCount skills (hooked=$($hookedSkills.Count), plain=$($plainSkills.Count))."
}
foreach ($skill in $hookedSkills) {
    $left = Join-Path $skill.FullName 'SKILL.md'
    $right = Join-Path (Join-Path $plain $skill.Name) 'SKILL.md'
    if (-not (Test-Path -LiteralPath $right)) { throw "Missing plain-profile skill: $($skill.Name)" }
    if ((Get-FileHash $left).Hash -ne (Get-FileHash $right).Hash) { throw "Profile skill mismatch: $($skill.Name)" }
    $parts = (Get-Content -LiteralPath $left -Raw) -split '(?m)^---\s*$', 3
    if ($parts.Count -lt 3 -or $parts[1] -notmatch '(?m)^name:\s*\S+' -or $parts[1] -notmatch '(?m)^description:\s*\S+') { throw "Invalid skill frontmatter: $left" }
    # Codex reads per-skill agents/openai.yaml; a missing one silently drops the skill on that host.
    foreach ($profileSkills in @($hooked, $plain)) {
        $manifest = Join-Path (Join-Path $profileSkills $skill.Name) 'agents/openai.yaml'
        if (-not (Test-Path -LiteralPath $manifest)) { throw "Missing Codex skill manifest: $manifest" }
    }
}
# Manifest version alignment: Claude and Codex hosts must advertise the SAME version for the
# same plugin, and both profiles must ship as one kit. Drift here is invisible to a host until a
# user compares them, so assert it (the .codex-plugin manifests sat a version behind for a month).
$manifestVersions = @{}
foreach ($profileName in @('programmer', 'programmer-skills')) {
    foreach ($manifestDir in @('.claude-plugin', '.codex-plugin')) {
        $manifestPath = Join-Path $root "plugins/$profileName/$manifestDir/plugin.json"
        if (-not (Test-Path -LiteralPath $manifestPath)) { throw "Missing plugin manifest: $manifestPath" }
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        if ($manifest.name -ne $profileName) { throw "Manifest name mismatch in $manifestPath (expected $profileName, found $($manifest.name))." }
        if (-not $manifest.repository) { throw "Manifest is missing the repository field: $manifestPath" }
        $manifestVersions["$profileName/$manifestDir"] = $manifest.version
    }
}

# Single source of truth for version: the plugin manifests. Both marketplaces must describe the
# same set of profiles but must NOT restate a version - a duplicated value drifts silently and is
# only noticed when a user compares the storefront against the installed plugin (it sat a minor
# version behind for weeks). Assert the duplicate cannot come back rather than keeping it in sync.
$marketplaceFiles = @(
    (Join-Path $root ".claude-plugin/marketplace.json"),
    (Join-Path $root ".agents/plugins/marketplace.json")
)
foreach ($marketplacePath in $marketplaceFiles) {
    if (-not (Test-Path -LiteralPath $marketplacePath)) { throw "Missing marketplace file: $marketplacePath" }
    $marketplace = Get-Content -LiteralPath $marketplacePath -Raw | ConvertFrom-Json
    $entryNames = @($marketplace.plugins | ForEach-Object { $_.name } | Sort-Object)
    $expectedNames = @("programmer", "programmer-skills")
    if (Compare-Object $entryNames $expectedNames) {
        throw "$marketplacePath advertises [$($entryNames -join ', ')] but the repo ships [$($expectedNames -join ', ')]."
    }
    foreach ($entry in $marketplace.plugins) {
        if ($entry.PSObject.Properties.Name -contains "version") {
            throw "$marketplacePath entry '$($entry.name)' restates a version; the plugin manifest is the only source of truth."
        }
        $sourcePath = if ($entry.source -is [string]) { $entry.source } else { $entry.source.path }
        $resolved = Join-Path $root ($sourcePath -replace "^\./", "")
        if (-not (Test-Path -LiteralPath $resolved)) { throw "$marketplacePath entry '$($entry.name)' points at a missing source: $sourcePath" }
    }
}
$distinctVersions = @($manifestVersions.Values | Sort-Object -Unique)
if ($distinctVersions.Count -ne 1) {
    $detail = ($manifestVersions.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ', '
    throw "All plugin manifests must advertise one kit version but found: $detail"
}

foreach ($json in Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.json') {
    $null = Get-Content -LiteralPath $json.FullName -Raw | ConvertFrom-Json
}
# Host census, exact and intentional like the skill count above: add the host here when a new
# adapter ships, so a dropped fragment fails the build instead of silently narrowing host coverage.
$expectedFragments = @('claude-hooks.fragment.json', 'codex-hooks.fragment.json', 'grok-hooks.fragment.json')
$fragments = @(Get-ChildItem -LiteralPath (Join-Path $root 'plugins/programmer/hooks/opt-in') -File -Filter '*hooks.fragment.json')
$fragmentNames = @($fragments.Name | Sort-Object)
if (Compare-Object $fragmentNames ($expectedFragments | Sort-Object)) {
    throw "Expected opt-in hook fragments $($expectedFragments -join ', ') but found $($fragmentNames -join ', ')."
}
foreach ($fragment in $fragments) {
    $host_ = $fragment.Name -replace '-hooks\.fragment\.json$', ''
    $adapter = Join-Path $root "plugins/programmer/hooks/opt-in/adapters/$host_/hook_adapter.py"
    if (-not (Test-Path -LiteralPath $adapter)) { throw "Hook fragment $($fragment.Name) has no adapter at $adapter" }
}
foreach ($fragment in $fragments) {
    if ((Get-Content -LiteralPath $fragment.FullName -Raw) -notmatch '__PLUGIN_ROOT__') { throw "Hook fragment is not portable: $($fragment.Name)" }
}
foreach ($file in Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object Extension -in '.md','.py','.ps1','.json','.yml','.yaml') {
    if ((Get-Content -LiteralPath $file.FullName -Raw) -match '[\uD83C-\uDBFF][\uDC00-\uDFFF]') { throw "Emoji or supplementary glyph found: $($file.FullName)" }
}
Write-Host 'Repository validation passed: JSON, skill frontmatter, profile parity, Codex skill manifests, host fragment/adapter census, inert hook tokens, and no-emoji policy.'
