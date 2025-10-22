@echo off
setlocal
rem Thin wrapper to call scripts\spec-easy.cmd from repo root
call "%~dp0scripts\spec-easy.cmd" %*
endlocal

