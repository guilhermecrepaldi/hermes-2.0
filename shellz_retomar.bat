@echo off
title Shellz - Retomar
echo ========================================
echo  🐚 SHELLZ - Retomar Ollama
echo ========================================
echo.
echo Iniciando servidor Ollama...

REM Verificar se ja esta rodando
tasklist /FI "IMAGENAME eq ollama.exe" /NH 2>nul | find /I "ollama.exe" >nul
if not errorlevel 1 (
    echo [OK] Ollama ja esta rodando.
    goto :fim
)

REM Iniciar Ollama via VBS (invisivel)
wscript.exe /B "D:\projetos\hermes-watchdog\ollama_invisible.vbs"
if errorlevel 1 (
    echo [ERRO] Falha ao iniciar Ollama.
    pause
    exit /b 1
)

echo Aguardando Ollama ficar pronto...
for /l %%i in (1,1,10) do (
    timeout /t 2 /nobreak >nul
    curl -s http://localhost:11434/api/version >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Ollama rodando em http://localhost:11434
        goto :fim
    )
)

echo [AVISO] Ollama pode nao ter iniciado completamente.
echo Verifique com: tasklist | find "ollama"

:fim
echo.
echo ========================================
echo  ✅ Shell 1 pronto para uso!
echo ========================================
echo.
pause
