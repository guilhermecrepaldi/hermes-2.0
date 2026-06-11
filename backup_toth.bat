@echo off
REM ============================================
REM BACKUP DO SISTEMA TOP OF THE HOUR
REM Gera: backup_toth_YYYY-MM-DD_HHMM.zip na Area de Trabalho
REM ============================================
setlocal enabledelayedexpansion

REM Pega data/hora no formato ISO
for /f "tokens=1-3 delims=/" %%a in ("%DATE%") do (
    set YY=%%c
    set MM=%%a
    set DD=%%b
)
for /f "tokens=1-2 delims=: " %%a in ("%TIME%") do (
    set HH=%%a
    set MI=%%b
)
if "%HH:~0,1%"==" " set HH=0%HH:~1,1%
set BACKUP_NAME=backup_toth_%YY%-%MM%-%DD%_%HH%%MI%
set BACKUP_DIR=%USERPROFILE%\Desktop\%BACKUP_NAME%

echo ===== BACKUP DO SISTEMA TOP OF THE HOUR =====
echo Destino: %BACKUP_DIR%

REM Criar estrutura
mkdir "%BACKUP_DIR%\hermes\config" 2>nul
mkdir "%BACKUP_DIR%\hermes\skills" 2>nul
mkdir "%BACKUP_DIR%\hermes\cron" 2>nul
mkdir "%BACKUP_DIR%\hermes\memory" 2>nul
mkdir "%BACKUP_DIR%\hermes\profiles" 2>nul
mkdir "%BACKUP_DIR%\hermes\gateway" 2>nul

REM 1. Projeto
echo [1/5] Projeto TOP OF THE HOUR...
if exist "D:\projetos\TOP OF THE HOUR - IA" (
    xcopy /E /I /Y "D:\projetos\TOP OF THE HOUR - IA" "%BACKUP_DIR%\projeto\" >nul
    echo   OK - projeto
) else (
    echo   AVISO: pasta do projeto nao encontrada
)

REM 2. Config Hermes (completa)
echo [2/5] Configuracao Hermes...
set HERMES_DIR=%USERPROFILE%\AppData\Local\hermes
if exist "%HERMES_DIR%\config.yaml" (
    copy "%HERMES_DIR%\config.yaml" "%BACKUP_DIR%\hermes\config\" >nul
    echo   OK - config.yaml
)
if exist "%HERMES_DIR%\.env" (
    copy "%HERMES_DIR%\.env" "%BACKUP_DIR%\hermes\config\" >nul
    echo   OK - .env
)
if exist "%HERMES_DIR%\auth.json" (
    copy "%HERMES_DIR%\auth.json" "%BACKUP_DIR%\hermes\config\" >nul
    echo   OK - auth.json
)
if exist "%HERMES_DIR%\channel_directory.json" (
    copy "%HERMES_DIR%\channel_directory.json" "%BACKUP_DIR%\hermes\config\" >nul
    echo   OK - channel_directory.json
)
if exist "%HERMES_DIR%\gateway_state.json" (
    copy "%HERMES_DIR%\gateway_state.json" "%BACKUP_DIR%\hermes\gateway\" >nul
    echo   OK - gateway_state.json
)
if exist "%HERMES_DIR%\hooks" (
    xcopy /E /I /Y "%HERMES_DIR%\hooks" "%BACKUP_DIR%\hermes\config\hooks\" >nul
    echo   OK - hooks
)

REM 3. Skills (TODOS)
echo [3/5] Skills...
if exist "%HERMES_DIR%\skills" (
    xcopy /E /I /Y "%HERMES_DIR%\skills" "%BACKUP_DIR%\hermes\skills\" >nul
    echo   OK - skills (completos)
)

REM 4. Cron
echo [4/5] Cron jobs...
if exist "%HERMES_DIR%\cron" (
    xcopy /E /I /Y "%HERMES_DIR%\cron" "%BACKUP_DIR%\hermes\cron\" >nul
    echo   OK - cron
)

REM 5. Memoria persistente + perfil
echo [5/5] Memoria e perfis...
if exist "%USERPROFILE%\.hermes\memory" (
    xcopy /E /I /Y "%USERPROFILE%\.hermes\memory" "%BACKUP_DIR%\hermes\memory\" >nul
    echo   OK - memoria persistente
)
if exist "%HERMES_DIR%\profiles" (
    xcopy /E /I /Y "%HERMES_DIR%\profiles" "%BACKUP_DIR%\hermes\profiles\" >nul
    echo   OK - profiles
)

REM 6. Version info
echo Versao: Edicao #001 - 10 Jun 2026 > "%BACKUP_DIR%\version.txt"
echo Gerado em: %DATE% %TIME% >> "%BACKUP_DIR%\version.txt"

REM 7. Compactar
echo.
echo Compactando para ZIP...
cd /d "%USERPROFILE%\Desktop"
powershell -Command "Compress-Archive -Path '%BACKUP_DIR%' -DestinationPath '%BACKUP_NAME%.zip' -Force"

if exist "%BACKUP_NAME%.zip" (
    echo.
    echo ===== BACKUP CONCLUIDO COM SUCESSO =====
    for %%F in ("%BACKUP_NAME%.zip") do echo Arquivo: %%F (%%~zF bytes)
    echo.
    echo Conteudo:
    powershell -Command "$z = [System.IO.Compression.ZipFile]::OpenRead('%BACKUP_NAME%.zip'); $z.Entries | Group-Object { \$_.FullName.Split('/')[0] } | Sort-Object Count -Desc | ForEach-Object { Write-Host ('  ' + \$_.Name + ': ' + \$_.Count + ' arquivos') -ForegroundColor Yellow }; $z.Dispose()"
) else (
    echo ERRO: Falha ao criar ZIP
)

REM Limpar
rmdir /S /Q "%BACKUP_DIR%" 2>nul

echo.
echo Pressione qualquer tecla para sair...
pause >nul