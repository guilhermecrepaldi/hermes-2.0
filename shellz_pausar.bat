@echo off
title Shellz - Pausar
echo ========================================
echo  🐚 SHELLZ - Pausar Ollama
echo ========================================
echo.
echo Parando servidor Ollama para liberar GPU...

REM 1. Parar o Ollama serve
tasklist /FI "IMAGENAME eq ollama.exe" /NH 2>nul | find /I "ollama.exe" >nul
if errorlevel 1 (
    echo [OK] Ollama ja estava parado.
) else (
    taskkill /F /IM ollama.exe >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Nao foi possivel parar o Ollama.
    ) else (
        echo [OK] Ollama parado.
    )
)

REM 2. Aguardar processo morrer
timeout /t 2 /nobreak >nul

REM 3. Liberar memoria GPU (se NVIDIA)
where nvidia-smi >nul 2>&1
if not errorlevel 1 (
    echo Limpando cache da GPU...
    nvidia-smi --gpu-reset >nul 2>&1
    if not errorlevel 1 (
        echo [OK] GPU liberada.
    )
)

echo.
echo ========================================
echo  ✅ GPU liberada! Aproveite o jogo.
echo ========================================
echo.
echo Para retomar: execute shellz_retomar.bat
echo.

pause
