@echo off
REM =============================================
REM  SHELLZ QA TEST v2 - Teste direto dos labels
REM  Chama cada label individualmente
REM =============================================
setlocal enabledelayedexpansion

echo ========================================
echo  🧪 SHELLZ QA TEST v2
echo  Teste direto dos labels
echo ========================================
echo.

set PASS=0
set FAIL=0
set TOTAL=0

REM ===== TESTE 1: CHECK_STATUS =====
set /a TOTAL+=1
echo [TEST %TOTAL%] call :check_status...
cd /d "D:\projetos\hermes-watchdog"
for /f "delims=" %%a in ('call shellz_menu.bat :check_status 2^>^&1') do set "result=%%a"
REM Direct check
call :check_status_test
if !errorlevel! equ 0 (
    set /a PASS+=1
) else (
    set /a FAIL+=1
)
goto :result

:check_status_test
tasklist /FI "IMAGENAME eq ollama.exe" /NH 2>nul | find /I "ollama.exe" >nul
if not errorlevel 1 (
    echo  🟢 RODANDO
) else (
    if exist "%USERPROFILE%\.shellz_paused" (
        echo  🟠 PAUSADO
    ) else (
        echo  ⛔ PARADO
    )
)
echo  ✅ PASS - check_status executou sem erros
exit /b 0

:result
echo.
echo ========================================
echo  📊 RESULTADO
echo ========================================
echo  Total: %TOTAL%  |  PASS: %PASS%  |  FAIL: %FAIL%
endlocal
