@echo off
title Neo Hermes — Preparar Ambiente
cd /d "%~dp0.."
echo.
echo  ========================================
echo    Neo Hermes — Preparando Ambiente
echo  ========================================
echo.
python watchdog\prepare_env.py --fix %*
echo.
if %ERRORLEVEL% equ 0 (
    echo  ✅ Ambiente pronto!
) else (
    echo  ⚠  Alguns checks falharam. Verifique acima.
)
echo.
pause
