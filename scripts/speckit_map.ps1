param(
  [Parameter(Mandatory=$true)][string]$Id,
  [string]$Capability = 'platform',
  [switch]$NoDesign,
  [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-Template([string]$name) {
  $path = Join-Path '.speckit/templates/openspec' $name
  if (-not (Test-Path $path)) { throw "Template not found: $path" }
  return Get-Content -Raw -LiteralPath $path
}

function Write-File([string]$path, [string]$content) {
  $dir = Split-Path -Parent $path
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  if ((Test-Path $path) -and -not $Force) { throw "File exists: $path (use -Force to overwrite)" }
  Set-Content -LiteralPath $path -Value $content -NoNewline
}

Write-Host "Scaffolding OpenSpec change from SpecKit templates..." -ForegroundColor Cyan

$changeRoot = Join-Path 'openspec/changes' $Id
$specRoot = Join-Path $changeRoot (Join-Path 'specs' $Capability)

# Load templates
$proposalTpl = Resolve-Template 'proposal-skeleton.md'
$tasksTpl    = (Resolve-Template 'tasks-skeleton.md').Replace('{{change_id}}', $Id)
$specTpl     = (Resolve-Template 'delta-spec-skeleton.md').Replace('{{change_id}}', $Id).Replace('{{requirement_title}}','SpecKit Integration')

Write-File (Join-Path $changeRoot 'proposal.md') $proposalTpl
Write-File (Join-Path $changeRoot 'tasks.md') $tasksTpl
Write-File (Join-Path $specRoot 'spec.md') $specTpl

if (-not $NoDesign) {
  $designTpl = Resolve-Template 'design-skeleton.md'
  Write-File (Join-Path $changeRoot 'design.md') $designTpl
}

Write-Host "Created change at: $changeRoot" -ForegroundColor Green
Write-Host "Next: Fill proposal/tasks/specs from SpecKit outputs, then run:" -ForegroundColor Yellow
Write-Host "  openspec validate $Id --strict" -ForegroundColor Yellow

