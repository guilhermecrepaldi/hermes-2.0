@echo off
title Shellz
mode con cols=65 lines=20
color 0A

:menu
cls
echo ============================================================
echo                  🐚  SHELLZ  🐚
echo        Controle do Ollama - Pausar/Retomar GPU
echo ============================================================
echo.
echo  Status:
call :check_status
echo.
echo  [1] 🟢 INICIAR Ollama (Shell 1)
echo  [2] ⏸  PAUSAR Ollama (liberar GPU para jogos)
echo  [3] ▶  RETOMAR Ollama (reativar Shell 1)
echo  [4] 📊 Ver Status completo
echo  [5] 🖥️  Abrir Shellz Tray (icone na bandeja)
echo  [6] ❌ Sair
echo.
set /p opt="Escolha: "

if "%opt%"=="1" goto :iniciar
if "%opt%"=="2" goto :pausar
if "%opt%"=="3" goto :retomar
if "%opt%"=="4" goto :status
if "%opt%"=="5" goto :tray
if "%opt%"=="6" exit
goto :menu

:iniciar
echo.
echo Iniciando Ollama...
wscript.exe /B "D:\projetos\hermes-watchdog\ollama_invisible.vbs"
timeout /t 3 /nobreak >nul
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if errorlevel 1 (
    echo [ERRO] Ollama nao iniciou.
) else (
    echo [OK] Ollama rodando em background.
)
timeout /t 2 /nobreak >nul
goto :menu

:pausar
echo.
echo Parando Ollama e liberando GPU...
if exist "%USERPROFILE%\.shellz_paused" (
    echo [OK] Ollama ja estava pausado.
    timeout /t 2 /nobreak >nul
    goto :menu
)
taskkill /F /IM ollama.exe >nul 2>&1
echo > "%USERPROFILE%\.shellz_paused" Pausado pelo usuario em %date% %time%
echo [OK] Ollama parado. GPU livre para jogos!
timeout /t 2 /nobreak >nul
goto :menu

:retomar
echo.
echo Iniciando Ollama novamente...
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if not errorlevel 1 (
    echo [OK] Ollama ja esta rodando.
) else (
    wscript.exe /B "D:\projetos\hermes-watchdog\ollama_invisible.vbs"
    timeout /t 4 /nobreak >nul
    tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
    if errorlevel 1 (
        echo [ERRO] Falha ao iniciar Ollama.
    ) else (
        echo [OK] Ollama rodando novamente.
    )
)
if exist "%USERPROFILE%\.shellz_paused" del "%USERPROFILE%\.shellz_paused"
timeout /t 2 /nobreak >nul
goto :menu

:status
cls
echo ============================================================
echo                  📊 STATUS SHELLZ
echo ============================================================
echo.
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if errorlevel 1 (echo  Shell 1 (Ollama):    ⛔ PARADO) else (echo  Shell 1 (Ollama):    🟢 RODANDO)
if exist "%USERPROFILE%\.shellz_paused" echo                         ⏸ PAUSADO PELO USUARIO

echo.
echo  Shell 2 (DeepSeek):  🟢 Online (via API)
echo  Shell 3 (Claude):    ⚪ Configurado (fallback)
echo.
tasklist /FI "IMAGENAME eq powershell.exe" 2>nul | find "shellz_tray" >nul
if errorlevel 1 (echo  Tray Icon:           ⛔ FECHADO) else (echo  Tray Icon:           🟢 ATIVO)
echo.
echo  Watchdog:            🟢 Ativo (cron 1min)
echo  GPU:                 Aguardando nvidia-smi...
for /f "tokens=2 delims=:" %%a in ('nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2^>nul') do echo                        %%a%% utilizada
echo.
echo  Modelo carregado:    qwen2.5-coder:7b (4.7GB)
echo  GitHub:              github.com/guilhermecrepaldi/hermes-2.0
echo.
pause
goto :menu

:tray
echo.
echo Iniciando icone na bandeja do Windows...
start "" wscript.exe /B "D:\projetos\hermes-watchdog\shellz_tray.vbs"
echo [OK] Icone Shellz deve aparecer na bandeja (ao lado do relogio).
echo.
echo Dicas:
echo - Clique ESQUERDO no icone: Pausar/Retomar
echo - Clique DIREITO no icone: Menu completo
echo.
echo Se nao aparecer, clique na setinha ^< para expandir a bandeja.
pause
goto :menu
