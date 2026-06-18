@echo off
title Hermes Watchdog — Anti-Travamento
echo ============================================
echo  Hermes Watchdog
echo  Monitoramento Anti-Travamento
echo ============================================
echo.
echo Iniciando watchdog em nova janela...
start "Hermes Watchdog" powershell -NoExit -Command "& { D:\projetos\hermes-watchdog\watchdog_hermes.ps1 }"
echo.
echo Watchdog iniciado. Feche esta janela se nao precisar mais.
echo.
echo Para verificar estado: Get-Content "$env:USERPROFILE\hermes-watchdog\watchdog_state.json"
echo.
pause