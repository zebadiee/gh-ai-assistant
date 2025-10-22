@echo off
setlocal
REM Run Easy Mode (interactive by default). Pass through any args.
call "%~dp0spec-easy.cmd" %*

REM Read last change id and start watcher in a new window
if not exist ".speckit\last_change_id.txt" (
  echo Could not determine change id (.speckit\last_change_id.txt missing). Exiting.
  exit /b 1
)
set /p ID=<".speckit\last_change_id.txt"
start powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0spec-watch.ps1" -Id "%ID%"
echo Watching started in a new window for change: %ID%
endlocal

