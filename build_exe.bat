@echo off
REM =============================================
REM  Hermes Workbench — Build Script
REM  Compila hermes_workbench.py em .exe unico
REM  Requer: pip install pyinstaller
REM =============================================
echo ========================================
echo  🏗️  Hermes Workbench — Build
echo ========================================
echo.

REM Find pyinstaller
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [ERRO] PyInstaller nao encontrado.
    echo Instale com: pip install pyinstaller
    pause
    exit /b 1
)

echo [1/3] Limpando build anterior...
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
del /f /q hermes-workbench.spec 2>nul

echo [2/3] Compilando executavel...
pyinstaller --onefile --name hermes-workbench --clean ^
    --add-data "s3_headroom.py;." ^
    --add-data "s3_grep.py;." ^
    --add-data "s1_router.py;." ^
    hermes_workbench.py

if errorlevel 1 (
    echo [ERRO] Falha na compilacao.
    pause
    exit /b 1
)

echo [3/3] Verificando...
dir dist\hermes-workbench.exe
echo.
echo ========================================
echo  ✅ EXE criado: dist\hermes-workbench.exe
echo  Tamanho: 
for %%F in (dist\hermes-workbench.exe) do echo  %%~zF bytes
echo ========================================
echo.
echo Para usar:
echo   dist\hermes-workbench.exe status
echo   dist\hermes-workbench.exe router "Criar funcao"
echo   dist\hermes-workbench.exe panorama D:\projeto
echo.
pause
