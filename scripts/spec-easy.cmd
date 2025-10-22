@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0spec-easy.ps1" %*
endlocal

