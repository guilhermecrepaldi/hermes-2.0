@echo off
chcp 65001 >nul
title Headroom + Ollama Auto-Start
echo ========================================
echo   Iniciando Headroom Proxy + Ollama
echo ========================================
echo.

REM =============================================
REM 1. INICIAR OLLAMA (se não estiver rodando)
REM =============================================
echo [1/3] Verificando Ollama...
curl -s http://localhost:11434/api/tags --max-time 3 >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Ollama ja rodando
) else (
    echo   🔄 Iniciando Ollama...
    start "" /B "C:\Users\Home\AppData\Local\Programs\Ollama\ollama.exe" serve
    echo   ✅ Ollama iniciado
)

REM =============================================
REM 2. INICIAR HEADROOM PROXY (se não estiver)
REM =============================================
echo [2/3] Verificando Headroom Proxy...
curl -s http://127.0.0.1:8787/health --max-time 3 >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Headroom Proxy ja rodando
) else (
    echo   🔄 Iniciando Headroom Proxy...
    start "" /B "C:\Users\Home\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" ^
        "C:\Users\Home\AppData\Local\hermes\hermes-agent\headroom_proxy.py" ^
        --port 8787 --upstream https://api.deepseek.com
    echo   ✅ Headroom Proxy iniciado
)

REM =============================================
REM 3. AGUARDAR E VERIFICAR
REM =============================================
echo [3/3] Aguardando servicos...
timeout /t 5 /nobreak >nul

echo.
echo Verificando Headroom...
curl -s http://127.0.0.1:8787/health
echo.
echo.
echo ✅ Ambiente pronto! Hermes Desktop pode ser iniciado.
echo.
echo NOTA: Se algo der errado, use rollback_headroom.bat
echo       para voltar ao DeepSeek direto.
