# Install HermesWatchdog as Windows Scheduled Task

$taskName = "HermesWatchdog"
$scriptPath = "D:\projetos\hermes-watchdog\watchdog_hermes.ps1"

# Check if already installed
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "[OK] Tareja $taskName ja existe. Estado: $($existing.State)"
    exit 0
}

# Set execution policy
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

# Create task action
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -NoExit -Command `"& '$scriptPath'`""

# Trigger: at user logon
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Settings: restart on failure, run on battery, etc.
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# Principal: run as current user with highest privileges
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest

# Register
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force

# Verify
$task = Get-ScheduledTask -TaskName $taskName
Write-Host "[OK] HermesWatchdog instalada. Estado: $($task.State)"
Write-Host "[OK] Inicia automaticamente ao fazer login."
Write-Host "[OK] Reinicia automaticamente se cair (3 tentativas, intervalo 1min)."

# Start now
Start-ScheduledTask -TaskName $taskName
Write-Host "[OK] Watchdog iniciado agora."

# Also start immediately as fallback
Start-Process powershell -WindowStyle Hidden -ArgumentList "-File `"$scriptPath`""
Write-Host "[OK] Watchdog tambem iniciado em processo independente."
