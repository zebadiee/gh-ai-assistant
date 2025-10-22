param(
  [Parameter(Mandatory=$false)][string]$Id = 'add-sample-feature',
  [int]$DebounceMs = 400
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Start-Validation([string]$changeId) {
  Write-Host ("[validate] openspec validate {0} --strict" -f $changeId) -ForegroundColor Yellow
  & openspec validate $changeId --strict
  $code = $LASTEXITCODE
  if ($code -eq 0) {
    Write-Host "[ok] Validation passed" -ForegroundColor Green
  } else {
    Write-Host "[warn] Validation failed — common fixes:" -ForegroundColor Red
    Write-Host " - Ensure top-level section: '## ADDED|MODIFIED|REMOVED Requirements'" -ForegroundColor Red
    Write-Host " - Each requirement needs '### Requirement: <name>'" -ForegroundColor Red
    Write-Host " - Each requirement needs at least one '#### Scenario:' with GIVEN/WHEN/THEN lines" -ForegroundColor Red
    Write-Host " - Prefer modifying existing specs over duplicating capabilities" -ForegroundColor Red
  }
}

$path = Join-Path 'openspec/changes' $Id
if (-not (Test-Path $path)) {
  throw "Change folder not found: $path"
}

Write-Host "Watching: $path (Ctrl+C to stop)" -ForegroundColor Cyan
Start-Validation -changeId $Id

$fsw = New-Object System.IO.FileSystemWatcher
$fsw.Path = $path
$fsw.Filter = '*.md'
$fsw.IncludeSubdirectories = $true
$fsw.EnableRaisingEvents = $true

$last = Get-Date 0

Register-ObjectEvent $fsw Changed -SourceIdentifier SpecChanged | Out-Null
Register-ObjectEvent $fsw Created -SourceIdentifier SpecCreated | Out-Null
Register-ObjectEvent $fsw Deleted -SourceIdentifier SpecDeleted | Out-Null
Register-ObjectEvent $fsw Renamed -SourceIdentifier SpecRenamed | Out-Null

try {
  while ($true) {
    $event = Wait-Event -Timeout 1
    if ($null -ne $event) {
      Remove-Event -EventIdentifier $event.EventIdentifier | Out-Null
      $now = Get-Date
      if (($now - $last).TotalMilliseconds -lt $DebounceMs) { continue }
      $last = $now
      Start-Validation -changeId $Id
    }
  }
} finally {
  Get-EventSubscriber | Where-Object { $_.SourceIdentifier -like 'Spec*' } | Unregister-Event -Force
}

