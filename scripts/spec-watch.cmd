@echo off
setlocal
set ID=%1
set "ROOT=%~dp0.."
if "%ID%"=="" (
  if exist "%ROOT%\.speckit\last_change_id.txt" (
    set /p ID=<"%ROOT%\.speckit\last_change_id.txt"
  )
)
if "%ID%"=="" (
  echo No change id provided and no .speckit\last_change_id.txt found.
  echo Usage: scripts\spec-watch.cmd ^<change-id^>
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0spec-watch.ps1" -Id "%ID%"
endlocal
