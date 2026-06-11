@echo off
title Hermes Watchdog — Instalador Automático
echo ============================================
echo  Instalando Watchdog como servico 24/7
echo ============================================
echo.

REM 1. Verificar se PowerShell ja pode rodar scripts
powershell -Command "Get-ExecutionPolicy -Scope CurrentUser" | findstr "RemoteSigned" >nul
if %errorlevel% neq 0 (
    echo [1/4] Configurando execution policy...
    powershell -Command "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force" >nul
) else (
    echo [1/4] Execution policy OK
)

REM 2. Criar tarefa no Windows Task Scheduler
echo [2/4] Criando tarefa no Windows Task Scheduler...

powershell -Command ^
"$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-WindowStyle Hidden -NoExit -Command \"& D:\projetos\hermes-watchdog\watchdog_hermes.ps1\"'; ^
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME; ^
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1); ^
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest; ^
Register-ScheduledTask -TaskName 'HermesWatchdog' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force; ^
Write-Host '  OK - Tarefa HermesWatchdog criada'"

echo.
echo [3/4] Iniciando watchdog agora...
start "" powershell -WindowStyle Hidden -Command "& D:\projetos\hermes-watchdog\watchdog_hermes.ps1"

echo [4/4] Verificando...
timeout /t 3 /nobreak >nul
powershell -Command ^
"$task = Get-ScheduledTask -TaskName 'HermesWatchdog' -ErrorAction SilentlyContinue; ^
if ($task) { Write-Host ('  OK - Task Scheduler: ' + $task.State) } else { Write-Host '  ERRO: Tarefa nao encontrada' }; ^
$proc = Get-Process -Name 'powershell' -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'watchdog_hermes' }; ^
if ($proc) { Write-Host ('  OK - Watchdog rodando (PID=' + $proc.Id + ')') } else { Write-Host '  ERRO: Watchdog nao rodando' }"

echo.
echo ============================================
echo  INSTALACAO CONCLUIDA
echo ============================================
echo.
echo  O watchdog:
echo  - Inicia automaticamente ao fazer login
echo  - Roda 24/7 em background (janela oculta)
echo  - Monitora Hermes a cada 30s
echo  - Se travar: kill + recovery em ate 5min
echo  - Se watchdog cair: Task Scheduler reativa
echo.
echo  Para ver status: 
echo    Get-ScheduledTask HermesWatchdog
echo    Get-Content "$env:USERPROFILE\hermes-watchdog\watchdog_state.json"
echo.
pause