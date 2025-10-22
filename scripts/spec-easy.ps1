param(
  [string]$DefaultId = 'add-sample-feature',
  [string]$DefaultCapability = 'platform',
  [string]$Id,
  [string]$Capability,
  [switch]$WithDecisionLog,
  [switch]$WithPivot,
  [switch]$NonInteractive
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "OpenSpec Easy Mode" -ForegroundColor Cyan
Write-Host "Answer a few questions. I’ll do the rest." -ForegroundColor Cyan

if ($PSBoundParameters.ContainsKey('Id')) {
  $id = $Id
} elseif ($NonInteractive) {
  $id = $DefaultId
} else {
  $id = Read-Host ("Change ID (kebab-case) [`$DefaultId: $DefaultId`]")
  if ([string]::IsNullOrWhiteSpace($id)) { $id = $DefaultId }
}

# Simple sanitize: spaces→-, lowercase, remove invalid chars
$id = ($id.Trim().ToLower() -replace '\s+', '-') -replace '[^a-z0-9-]', ''
if ([string]::IsNullOrWhiteSpace($id)) { throw 'Invalid change id.' }

if ($PSBoundParameters.ContainsKey('Capability')) {
  $cap = $Capability
} elseif ($NonInteractive) {
  $cap = $DefaultCapability
} else {
  $cap = Read-Host ("Capability folder [`$DefaultCapability: $DefaultCapability`]")
  if ([string]::IsNullOrWhiteSpace($cap)) { $cap = $DefaultCapability }
}

if (-not $PSBoundParameters.ContainsKey('WithDecisionLog') -and -not $NonInteractive) {
  $useDecision = Read-Host "Add decision-log.md? (y/N)"
  if ($useDecision -match '^(y|yes)$') { $WithDecisionLog = $true }
}
if (-not $PSBoundParameters.ContainsKey('WithPivot') -and -not $NonInteractive) {
  $usePivot = Read-Host "Add pivot.md? (y/N)"
  if ($usePivot -match '^(y|yes)$') { $WithPivot = $true }
}

$paramMap = @{ Id = $id; Capability = $cap }
if ($WithDecisionLog) { $paramMap['WithDecisionLog'] = $true }
if ($WithPivot)       { $paramMap['WithPivot'] = $true }

Write-Host "\nScaffolding files..." -ForegroundColor Yellow
# Always resolve paths relative to this script's directory
$scriptDir = $PSScriptRoot
$repoRoot = Resolve-Path (Join-Path $scriptDir '..')
& (Join-Path $scriptDir 'speckit_map.ps1') @paramMap | Write-Output

Write-Host "\nChecking your work with strict validation..." -ForegroundColor Yellow
& openspec validate $id --strict | Write-Output

# Remember last change id for convenience launchers (at repo root)
try {
  $lastDir = Join-Path $repoRoot '.speckit'
  $lastIdPath = Join-Path $lastDir 'last_change_id.txt'
  if (-not (Test-Path $lastDir)) { New-Item -ItemType Directory -Path $lastDir -Force | Out-Null }
  Set-Content -LiteralPath $lastIdPath -Value $id -NoNewline
} catch {
  Write-Host "(warning) Could not write .speckit/last_change_id.txt" -ForegroundColor DarkYellow
}

Write-Host "\nAll set! Open these files and fill them in:" -ForegroundColor Green
$changeDir = Join-Path $repoRoot ("openspec/changes/" + $id)
Write-Host ("  {0}" -f (Join-Path $changeDir 'proposal.md'))
Write-Host ("  {0}" -f (Join-Path $changeDir 'tasks.md'))
if (Test-Path (Join-Path $changeDir 'design.md'))        { Write-Host ("  {0}" -f (Join-Path $changeDir 'design.md')) }
if (Test-Path (Join-Path $changeDir 'decision-log.md'))  { Write-Host ("  {0}" -f (Join-Path $changeDir 'decision-log.md')) }
if (Test-Path (Join-Path $changeDir 'pivot.md'))         { Write-Host ("  {0}" -f (Join-Path $changeDir 'pivot.md')) }
Write-Host ("  {0}" -f (Join-Path $changeDir ("specs/" + $cap + "/spec.md")))

Write-Host "\nNext steps:" -ForegroundColor Cyan
Write-Host "  1) Edit the files above (use Markdown preview)."
Write-Host "  2) Run: openspec validate $id --strict"
Write-Host "  3) After approval and implementation: openspec archive $id --yes"
