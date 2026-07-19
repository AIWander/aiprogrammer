$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$hooked = Join-Path $root 'plugins/programmer/skills'
$plain = Join-Path $root 'plugins/programmer-skills/skills'
$hookedSkills = @(Get-ChildItem -LiteralPath $hooked -Directory)
$plainSkills = @(Get-ChildItem -LiteralPath $plain -Directory)
if ($hookedSkills.Count -ne 5 -or $plainSkills.Count -ne 5) { throw 'Both profiles must contain exactly five skills.' }
foreach ($skill in $hookedSkills) {
    $left = Join-Path $skill.FullName 'SKILL.md'
    $right = Join-Path (Join-Path $plain $skill.Name) 'SKILL.md'
    if (-not (Test-Path -LiteralPath $right)) { throw "Missing plain-profile skill: $($skill.Name)" }
    if ((Get-FileHash $left).Hash -ne (Get-FileHash $right).Hash) { throw "Profile skill mismatch: $($skill.Name)" }
    $parts = (Get-Content -LiteralPath $left -Raw) -split '(?m)^---\s*$', 3
    if ($parts.Count -lt 3 -or $parts[1] -notmatch '(?m)^name:\s*\S+' -or $parts[1] -notmatch '(?m)^description:\s*\S+') { throw "Invalid skill frontmatter: $left" }
}
foreach ($json in Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.json') {
    $null = Get-Content -LiteralPath $json.FullName -Raw | ConvertFrom-Json
}
$fragments = @(Get-ChildItem -LiteralPath (Join-Path $root 'plugins/programmer/hooks/opt-in') -File -Filter '*hooks.fragment.json')
if ($fragments.Count -ne 2) { throw 'Expected Claude and Codex opt-in hook fragments.' }
foreach ($fragment in $fragments) {
    if ((Get-Content -LiteralPath $fragment.FullName -Raw) -notmatch '__PLUGIN_ROOT__') { throw "Hook fragment is not portable: $($fragment.Name)" }
}
foreach ($file in Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object Extension -in '.md','.py','.ps1','.json','.yml','.yaml') {
    if ((Get-Content -LiteralPath $file.FullName -Raw) -match '[\uD83C-\uDBFF][\uDC00-\uDFFF]') { throw "Emoji or supplementary glyph found: $($file.FullName)" }
}
Write-Host 'Repository validation passed: JSON, skill frontmatter, profile parity, inert hook tokens, and no-emoji policy.'
