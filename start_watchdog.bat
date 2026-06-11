@echo off
REM Inicia o Hermes Watchdog em segundo plano
REM Usado pelo atalho de Startup e pelo Task Scheduler

start /B /MIN powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\projetos\hermes-watchdog\watchdog_hermes.ps1"