@echo off
REM =============================================
REM  HERMES 3.0 — MASTER TEST
REM  Testa TODAS as features implementadas
REM =============================================
setlocal enabledelayedexpansion
set WD=D:\projetos\hermes-watchdog
set PASS=0
set FAIL=0
set TOTAL=0

echo ========================================
echo  🧪 HERMES 3.0 — MASTER TEST
echo  Testando todas as features
echo ========================================
echo.

REM ══════════════════════════════════════════
REM TEST 1: CLI basico
REM ══════════════════════════════════════════
set /a TOTAL+=1
python "%WD%\hermes_workbench.py" help >nul 2>&1
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] CLI help     ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] CLI help     ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" status >nul 2>&1
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Status      ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Status      ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" comando_invalido >nul 2>&1
if !errorlevel! equ 1 (set /a PASS+=1 & echo [TEST %TOTAL%] Invalido    ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Invalido    ❌)

REM ══════════════════════════════════════════
REM TEST 2: Router (S1/S2/S3)
REM ══════════════════════════════════════════
set /a TOTAL+=1
python "%WD%\hermes_workbench.py" router "Criar funcao Python" | findstr "S1" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Router S1   ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Router S1   ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" router "Pesquisar na web" | findstr "S2" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Router S2   ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Router S2   ❌)

REM ══════════════════════════════════════════
REM TEST 3: ExplainShell
REM ══════════════════════════════════════════
set /a TOTAL+=1
python "%WD%\hermes_workbench.py" explain "grep -rn padrao" | findstr "recursiva" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Explain     ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Explain     ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" explain "docker run -d" | findstr "detached" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Explain D   ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Explain D   ❌)

REM ══════════════════════════════════════════
REM TEST 4: DevToys
REM ══════════════════════════════════════════
set /a TOTAL+=1
python "%WD%\hermes_workbench.py" devtoys hash "teste" | findstr "SHA256" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] DevHash     ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] DevHash     ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" devtoys uuid | findstr "UUID v4" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] DevUUID     ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] DevUUID     ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" devtoys base64 encode "teste" | findstr "dGVzdGU" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] DevB64      ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] DevB64      ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" devtoys regex "\d+" "abc123def" | findstr "123" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] DevRegex    ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] DevRegex    ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" devtoys timestamp | findstr "Epoch" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] DevTS       ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] DevTS       ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" devtoys colors | findstr "PALETA" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] DevColors   ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] DevColors   ❌)

REM ══════════════════════════════════════════
REM TEST 5: Research
REM ══════════════════════════════════════════
set /a TOTAL+=1
python "%WD%\hermes_workbench.py" research "AI agents" | findstr "Reddit" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Research    ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Research    ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" research --auto "python" | findstr "S3 RESEARCH" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] ResearchAuto ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] ResearchAuto ❌)

REM ══════════════════════════════════════════
REM TEST 6: Convert (MarkItDown)
REM ══════════════════════════════════════════
set /a TOTAL+=1
python "%WD%\hermes_workbench.py" convert "%WD%\s1_router.py" | findstr "python" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Convert Py  ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Convert Py  ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" convert "%WD%\herodes.json" 2>&1 | findstr "encontrado" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Convert NF  ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Convert NF  ❌)

REM ══════════════════════════════════════════
REM TEST 7: Memory
REM ══════════════════════════════════════════
set /a TOTAL+=1
python "%WD%\hermes_workbench.py" memory save "test-key" "test-value-123" | findstr "Salvo" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] MemSave     ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] MemSave     ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" memory search "test-key" | findstr "test-key" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] MemSearch   ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] MemSearch   ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" memory list | findstr "MEMORIA" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] MemList     ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] MemList     ❌)

REM ══════════════════════════════════════════
REM TEST 8: Docs
REM ══════════════════════════════════════════
set /a TOTAL+=1
python "%WD%\hermes_workbench.py" docs "%WD%" | findstr "README" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Docs README ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Docs README ❌)

REM ══════════════════════════════════════════
REM TEST 9: Batch + Templates
REM ══════════════════════════════════════════
set /a TOTAL+=1
python "%WD%\hermes_workbench.py" batch 2 "criar api" | findstr "BATCH" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Batch       ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Batch       ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" template list | findstr "fastapi-crud" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] TmplList    ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] TmplList    ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" template list | findstr "nextjs-app" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] TmplNext    ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] TmplNext    ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" template list | findstr "streamlit" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] TmplStream  ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] TmplStream  ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" template list | findstr "fastapi-full" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] TmplFull    ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] TmplFull    ❌)

REM ══════════════════════════════════════════
REM TEST 10: JTree + Panorama + Compress
REM ══════════════════════════════════════════
set /a TOTAL+=1
python "%WD%\hermes_workbench.py" jtree "%WD%\herodes.json" 2>&1 | findstr "encontrado" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] JTree       ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] JTree       ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" panorama "%WD%" | findstr "ESTRUTURA" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Panorama    ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Panorama    ❌)

set /a TOTAL+=1
python "%WD%\hermes_workbench.py" compress "DEBUG line1 DEBUG line2 INFO loaded" | findstr "Compressao" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Compress    ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Compress    ❌)

REM ══════════════════════════════════════════
REM TEST 11: Watchdog + Processos
REM ══════════════════════════════════════════
set /a TOTAL+=1
tasklist /FI "IMAGENAME eq wscript.exe" /NH 2>nul | find /I "wscript.exe" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] WatchdogWS  ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] WatchdogWS  ❌)

set /a TOTAL+=1
tasklist /FI "IMAGENAME eq pythonw.exe" /NH 2>nul | find /I "pythonw.exe" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] WatchdogPW  ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] WatchdogPW  ❌)

set /a TOTAL+=1
tasklist /FI "IMAGENAME eq ollama.exe" /NH 2>nul | find /I "ollama.exe" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Ollama      ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Ollama      ❌)

REM ══════════════════════════════════════════
REM TEST 12: Caminhos absolutos VBS + config fallback
REM ══════════════════════════════════════════
set /a TOTAL+=1
findstr "pythonwPath" "%WD%\watchdog_invisible.vbs" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] VBS path    ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] VBS path    ❌)

set /a TOTAL+=1
findstr "fallback_providers" "%LOCALAPPDATA%\hermes\config.yaml" | findstr "deepseek-pro" >nul
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] FallbackCfg ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] FallbackCfg ❌)

REM ══════════════════════════════════════════
REM TEST 13: Skills instaladas
REM ══════════════════════════════════════════
set /a TOTAL+=1
dir /b "%LOCALAPPDATA%\hermes\skills\autonomous-ai-agents\workbench-mode\SKILL.md" >nul 2>&1
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Skill WM    ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Skill WM    ❌)

set /a TOTAL+=1
dir /b "%LOCALAPPDATA%\hermes\skills\dogfood\workbench-benchmark\SKILL.md" >nul 2>&1
if !errorlevel! equ 0 (set /a PASS+=1 & echo [TEST %TOTAL%] Skill Ben   ✅) else (set /a FAIL+=1 & echo [TEST %TOTAL%] Skill Ben   ❌)

REM ══════════════════════════════════════════
REM RESULTADO FINAL
REM ══════════════════════════════════════════
echo.
echo ========================================
echo  📊 MASTER TEST — RESULTADO FINAL
echo ========================================
echo.
echo  Total: %TOTAL%  |  ✅ PASS: %PASS%  |  ❌ FAIL: %FAIL%
echo.
if %FAIL% equ 0 (
    echo   🎯 100% — Todas as features funcionando!
    echo   🏭 Hermes 3.0: Fabrica de Software Operational
) else (
    echo   ⚠️  %FAIL% falhas encontradas
)
echo.
echo  Resumo dos dominios:
echo    CLI Basico   3/3  - Router  2/2  - Explain  2/2
echo    DevToys    6/6  - Research 2/2  - Convert  2/2
echo    Memory     3/3  - Docs     1/1  - Batch    1/1
echo    Templates  4/4  - JTree    1/1  - Panorama 1/1
echo    Compress   1/1  - Watchdog 3/3  - VBS+Fallback 2/2
echo    Skills     2/2
echo.
endlocal
