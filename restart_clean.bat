@echo off
title Shellz - Clean Restart
echo ========================================
echo  Limpando todos os watchdogs antigos
echo ========================================
echo.

echo [1/5] Matando wscript.exe (watchdogs antigos)...
taskkill /F /IM wscript.exe >nul 2>&1
echo OK

echo [2/5] Matando pythonw.exe (watchdogs velhos)...
taskkill /F /FI "IMAGENAME eq pythonw.exe" >nul 2>&1
echo OK

echo [3/5] Iniciando watchdog NOVO via VBS (caminho absoluto)...
start /B wscript.exe /B "D:\projetos\hermes-watchdog\watchdog_invisible.vbs"
echo OK

echo [4/5] Iniciando Shellz Tray...
start /B wscript.exe /B "D:\projetos\hermes-watchdog\shellz_tray_guardian.vbs"
echo OK

echo [5/5] Verificando...
timeout /t 3 /nobreak >nul
tasklist /FI "IMAGENAME eq wscript.exe" /NH 2>nul | find /I "wscript.exe"
echo wscript.exe rodando
tasklist /FI "IMAGENAME eq pythonw.exe" /NH 2>nul | find /I "pythonw.exe"
echo pythonw.exe rodando

echo.
echo ========================================
echo  ✅ Watchdog zerado. Zero janelas.
echo ========================================
echo.
echo Feche esta janela.
pause
