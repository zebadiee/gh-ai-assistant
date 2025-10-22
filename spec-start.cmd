@echo off
setlocal
rem Thin wrapper to call scripts\spec-start.cmd from repo root
call "%~dp0scripts\spec-start.cmd" %*
endlocal

