param(
  [string]$DefaultId = 'add-sample-feature',
  [string]$DefaultCapability = 'platform'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "OpenSpec Easy Mode" -ForegroundColor Cyan
Write-Host "Answer a few questions. I’ll do the rest." -ForegroundColor Cyan

$id = Read-Host ("Change ID (kebab-case) [`$DefaultId: $DefaultId`]")
if ([string]::IsNullOrWhiteSpace($id)) { $id = $DefaultId }

# Simple sanitize: spaces→-, lowercase, remove invalid chars
$id = ($id.Trim().ToLower() -replace '\s+', '-') -replace '[^a-z0-9-]', ''
if ([string]::IsNullOrWhiteSpace($id)) { throw 'Invalid change id.' }

$cap = Read-Host ("Capability folder [`$DefaultCapability: $DefaultCapability`]")
if ([string]::IsNullOrWhiteSpace($cap)) { $cap = $DefaultCapability }

$useDecision = Read-Host "Add decision-log.md? (y/N)"
$usePivot    = Read-Host "Add pivot.md? (y/N)"

$argsList = @('-Id', $id, '-Capability', $cap)
if ($useDecision -match '^(y|yes)$') { $argsList += '-WithDecisionLog' }
if ($usePivot -match '^(y|yes)$')    { $argsList += '-WithPivot' }

Write-Host "\nScaffolding files..." -ForegroundColor Yellow
& ./scripts/speckit_map.ps1 @argsList | Write-Output

Write-Host "\nChecking your work with strict validation..." -ForegroundColor Yellow
& openspec validate $id --strict | Write-Output

Write-Host "\nAll set! Open these files and fill them in:" -ForegroundColor Green
Write-Host "  openspec/changes/$id/proposal.md"
Write-Host "  openspec/changes/$id/tasks.md"
if (Test-Path "openspec/changes/$id/design.md") { Write-Host "  openspec/changes/$id/design.md" }
if (Test-Path "openspec/changes/$id/decision-log.md") { Write-Host "  openspec/changes/$id/decision-log.md" }
if (Test-Path "openspec/changes/$id/pivot.md") { Write-Host "  openspec/changes/$id/pivot.md" }
Write-Host "  openspec/changes/$id/specs/$cap/spec.md"

Write-Host "\nNext steps:" -ForegroundColor Cyan
Write-Host "  1) Edit the files above (use Markdown preview)."
Write-Host "  2) Run: openspec validate $id --strict"
Write-Host "  3) After approval and implementation: openspec archive $id --yes"

