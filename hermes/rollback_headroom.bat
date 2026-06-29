@echo off
chcp 65001 >nul
echo ========================================
echo   HeadRoom Hermes - Rollback Tool
echo ========================================
echo.
echo 1) Voltar config ao normal (DeepSeek direto)
echo 2) Matar proxy Headroom
echo 3) Sair
echo.
choice /c 123 /n /m "Escolha [1-3]: "
if errorlevel 3 exit /b
if errorlevel 2 goto kill
if errorlevel 1 goto restore

:restore
echo.
echo Restaurando config.yaml...
copy /Y config.yaml.bak.pre-headroom config.yaml
copy /Y .env.bak.pre-headroom .env
echo ✅ Configuracao restaurada - Hermes volta a falar direto com DeepSeek
echo.
echo Reinicie o Hermes (ou aguarde o proximo prompt)
goto end

:kill
echo.
echo Matando processos Headroom na porta 8787...
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8787 ^| findstr LISTENING') do (
    taskkill /F /PID %%i 2>nul
    echo   Matado PID %%i
)
echo ✅ Proxy Headroom encerrado
goto end

:end
echo.
echo Pronto! Rollback concluido.
pause
