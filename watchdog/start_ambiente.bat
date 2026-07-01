@echo off
chcp 65001 >nul
title Neo Hermes — Ambiente de Trabalho
cd /d "%~dp0"

echo ========================================
echo   🏠 NEO HERMES — Iniciando Ambiente
echo ========================================
echo.

REM ============================================
REM 1. INICIAR OLLAMA (se não estiver rodando)
REM ============================================
echo [1/3] Verificando Ollama...
curl -sf http://localhost:11434/api/version >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Ollama ja esta rodando!
) else (
    echo   ⏳ Iniciando Ollama em background...
    start /B "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    timeout /t 5 /nobreak >nul
    curl -sf http://localhost:11434/api/version >nul 2>&1
    if %errorlevel% equ 0 (
        echo   ✅ Ollama iniciado com sucesso!
    ) else (
        echo   ❌ Falha ao iniciar Ollama. Inicie manualmente.
    )
)
echo.

REM ============================================
REM 2. VERIFICAR MODELO S1
REM ============================================
echo [2/3] Verificando modelo S1 (qwen2.5-coder:7b)...
curl -sf http://localhost:11434/api/tags 2>&1 | findstr "qwen2.5-coder:7b" >nul
if %errorlevel% equ 0 (
    echo   ✅ Modelo S1 disponivel!
) else (
    echo   ⚠️  Modelo S1 nao encontrado. Baixando...
    "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" pull qwen2.5-coder:7b
)
echo.

REM ============================================
REM 3. VERIFICAR OPENCLI
REM ============================================
echo [3/3] Verificando OpenCLI...
where opencli >nul 2>&1
if %errorlevel% equ 0 (
    opencli doctor 2>&1 | findstr "connected" >nul
    if %errorlevel% equ 0 (
        echo   ✅ OpenCLI conectado!
    ) else (
        echo   ⚠️  OpenCLI instalado, mas extensao Chrome desconectada
    )
) else (
    echo   ❌ OpenCLI nao instalado. Execute: npm install -g @jackwener/opencli
)
echo.

REM ============================================
REM RESUMO
REM ============================================
echo ========================================
echo   🏠 AMBIENTE PRONTO
echo ========================================
echo   DeepSeek V4 Flash + Ollama S1
echo   Headroom: ❌ Removido
echo   Proxy:    ❌ Nenhum
echo   Custo:    $0 para tarefas S1
echo ========================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
