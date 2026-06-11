@echo off
REM Hermes 2.0 - Watchdog Guardian (INVISIVEL)
REM Executado pelo cron a CADA MINUTO via Hermes cron
REM Nao abre nenhuma janela - usa VBS launcher

set "WATCHDIR=%USERPROFILE%\hermes-watchdog"
set "WATCHLOG=%WATCHDIR%\logs\guardian_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log"

if not exist "%WATCHDIR%\logs" mkdir "%WATCHDIR%\logs"

REM Verificar se watchdog esta rodando (pelo processo wscript.exe que lancou o VBS)
tasklist /FI "WINDOWTITLE eq HermesWatchdog*" /NH 2>nul | find /I "cmd.exe" >nul
if errorlevel 1 (
    REM Checar processo watchdog_hermes.bat
    wmic process where "name='cmd.exe' and commandline like '%%watchdog%%'" get processid 2>nul | findstr /r "^[0-9]" >nul
    if errorlevel 1 (
        REM Watchdog NAO esta rodando - iniciar via VBS (invisivel)
        wscript.exe /B "D:\projetos\hermes-watchdog\watchdog_invisible.vbs"
        echo [%date% %time%] [GUARDIAN] Watchdog nao encontrado. Iniciado (invisivel). >> "%WATCHLOG%"
    )
)

REM Verificar Ollama - mas apenas se NAO estiver pausado pelo usuario
if not exist "%USERPROFILE%\.shellz_paused" (
    tasklist /FI "IMAGENAME eq ollama.exe" /NH 2>nul | find /I "ollama.exe" >nul
    if errorlevel 1 (
        REM Ollama NAO esta rodando - reiniciar
        wscript.exe /B "D:\projetos\hermes-watchdog\ollama_invisible.vbs"
        echo [%date% %time%] [GUARDIAN] Ollama reiniciado (nao estava rodando). >> "%WATCHLOG%"
    )
)

REM Recriar atalho de startup se foi deletado (agora usando VBS invisivel)
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\HermesWatchdog.lnk" (
    powershell -NoProfile -Command ^
    "$wshell = New-Object -ComObject WScript.Shell; ^
    $s = $wshell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\HermesWatchdog.lnk'); ^
    $s.TargetPath = 'wscript.exe'; ^
    $s.Arguments = '/B "D:\projetos\hermes-watchdog\watchdog_invisible.vbs"'; ^
    $s.Description = 'Hermes 2.0 - Watchdog 24/7 (Invisivel)'; ^
    $s.WorkingDirectory = 'D:\projetos\hermes-watchdog'; ^
    $s.WindowStyle = 7; ^
    $s.IconLocation = '%SystemRoot%\System32\wbem\wmiprvse.exe,0'; ^
    $s.Save()" >nul
    echo [%date% %time%] [GUARDIAN] Atalho de startup recriado. >> "%WATCHLOG%"
)

exit /b 0
