@echo off
setlocal
rem Thin wrapper to call scripts\spec-watch.cmd from repo root
call "%~dp0scripts\spec-watch.cmd" %*
endlocal

