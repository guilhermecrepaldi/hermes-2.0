@echo off
setlocal enabledelayedexpansion

REM =============================================
REM  HERMES WATCHDOG - Auto Health Check
REM  Roda a cada 5 minutos (loop batch puro)
REM  100% batch - zero PowerShell
REM  Iniciado pelo watchdog_invisible.vbs (wscript, zero janelas)
REM =============================================

set "WATCHDIR=%USERPROFILE%\hermes-watchdog"
set "LOGDIR=%WATCHDIR%\logs"
set "HERMES_LOG=%USERPROFILE%\AppData\Local\hermes\logs\agent.log"
set "INTERVAL_SEC=300"
set "OLLAMA_EXE=C:\Users\Home\AppData\Local\Programs\Ollama\ollama.exe"
set "PAUSE_FLAG=%USERPROFILE%\.shellz_paused"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"
if not exist "%WATCHDIR%" mkdir "%WATCHDIR%"

echo [%date% %time%] [INFO] Hermes Watchdog iniciado >> "%LOGDIR%\watchdog_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log"

:loop

REM --------------------------------------------------
REM 1. Hermes esta rodando?
REM --------------------------------------------------
tasklist /FI "IMAGENAME eq node.exe" /NH 2>nul | find /I "node.exe" >nul
if errorlevel 1 (
    call :save_state idle "hermes_not_running"
    goto :check_ollama
)

REM --------------------------------------------------
REM 2. Log foi modificado nos ultimos 25 min?
REM --------------------------------------------------
set "LOG_MODIFIED="
set "NOW_MIN="
set "LOG_MIN="

if exist "%HERMES_LOG%" (
    for %%F in ("%HERMES_LOG%") do set "LOG_MODIFIED=%%~tF"
    for /f "tokens=1-2 delims=: " %%a in ("%LOG_MODIFIED%") do (
        set /a "LOG_HH=%%a", "LOG_MM=%%b" 2>nul
    )
    for /f "tokens=1-2 delims=: " %%a in ("%time%") do (
        set /a "NOW_HH=%%a", "NOW_MM=%%b" 2>nul
    )
    
    REM Calcular diferenca em minutos (aproximado)
    set /a "DIFF_HH=NOW_HH-LOG_HH", "DIFF_MM=NOW_MM-LOG_MM" 2>nul
    if !DIFF_HH! lss 0 set /a "DIFF_HH+=24"
    set /a "DIFF_TOTAL=DIFF_HH*60+DIFF_MM" 2>nul
    
    if defined DIFF_TOTAL (
        if !DIFF_TOTAL! gtr 25 (
            echo [%date% %time%] [WARN] TRAVADO: Log nao atualizado ha !DIFF_TOTAL!min >> "%LOGDIR%\watchdog_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log"
            call :recover "log_stale_!DIFF_TOTAL!min"
            goto :check_ollama
        )
    )
)

call :save_state healthy monitoring
goto :check_ollama

REM --------------------------------------------------
REM 3. OLLAMA HEALTH CHECK (so se nao estiver pausado)
REM --------------------------------------------------
:check_ollama
if not exist "%PAUSE_FLAG%" (
    tasklist /FI "IMAGENAME eq ollama.exe" /NH 2>nul | find /I "ollama.exe" >nul
    if errorlevel 1 (
        echo [%date% %time%] [OLLAMA] Reiniciando (nao estava rodando) >> "%LOGDIR%\guardian_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log"
        start /B "" "%OLLAMA_EXE%" serve
    )
)

REM --------------------------------------------------
REM 4. STARTUP SHORTCUTS
REM --------------------------------------------------
:check_shortcuts
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\HermesWatchdog.lnk" (
    echo [%date% %time%] [SHORTCUT] Recriando HermesWatchdog.lnk >> "%LOGDIR%\guardian_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log"
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$wshell = New-Object -ComObject WScript.Shell; ^
    $s = $wshell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\HermesWatchdog.lnk'); ^
    $s.TargetPath = 'wscript.exe'; ^
    $s.Arguments = '/B \"D:\projetos\hermes-watchdog\watchdog_invisible.vbs\"'; ^
    $s.Description = 'Hermes 2.0 - Watchdog 24/7'; ^
    $s.WorkingDirectory = 'D:\projetos\hermes-watchdog'; ^
    $s.WindowStyle = 7; ^
    $s.Save()" >nul 2>&1
)

if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ShellzTray.lnk" (
    echo [%date% %time%] [SHORTCUT] Recriando ShellzTray.lnk >> "%LOGDIR%\guardian_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log"
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$wshell = New-Object -ComObject WScript.Shell; ^
    $s = $wshell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\ShellzTray.lnk'); ^
    $s.TargetPath = 'wscript.exe'; ^
    $s.Arguments = '/B \"D:\projetos\hermes-watchdog\shellz_tray_guardian.vbs\"'; ^
    $s.Description = 'Shellz Tray - Pausar/Retomar Ollama'; ^
    $s.WorkingDirectory = 'D:\projetos\hermes-watchdog'; ^
    $s.WindowStyle = 7; ^
    $s.Save()" >nul 2>&1
)

:sleep
REM Delay de 5 minutos
ping -n %INTERVAL_SEC% 127.0.0.1 >nul
goto :loop

REM ===== FUNCOES =====

:save_state
echo {>"%WATCHDIR%\watchdog_state.json"
echo   "timestamp": "%date% %time%",>>"%WATCHDIR%\watchdog_state.json"
echo   "status": "%1",>>"%WATCHDIR%\watchdog_state.json"
echo   "action": "%2">>"%WATCHDIR%\watchdog_state.json"
echo }>>"%WATCHDIR%\watchdog_state.json"
exit /b 0

:recover
echo [%date% %time%] [WARN] Matando Hermes (node.exe)... >> "%LOGDIR%\watchdog_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log"
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *hermes*" 2>nul
if defined HERMES_PID taskkill /F /PID !HERMES_PID! 2>nul
call :save_state recovery "killed_%~1"
echo [%date% %time%] [WARN] Hermes finalizado. Recovery pronto. >> "%LOGDIR%\watchdog_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log"
exit /b 0
