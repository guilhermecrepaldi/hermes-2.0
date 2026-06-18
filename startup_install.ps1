# Cria atalho do Hermes Watchdog na pasta Startup
# Isso faz o watchdog iniciar automaticamente ao fazer login
# Nao precisa de admin - funciona para o usuario atual

$wshell = New-Object -ComObject WScript.Shell
$startup = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startup "HermesWatchdog.lnk"
$scriptPath = "D:\projetos\hermes-watchdog\watchdog_hermes.ps1"

$shortcut = $wshell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-WindowStyle Hidden -NoExit -File `"$scriptPath`""
$shortcut.Description = "Hermes Watchdog - Anti-Travamento 24/7"
$shortcut.WorkingDirectory = "D:\projetos\hermes-watchdog"
$shortcut.Save()

Write-Host "[OK] Atalho criado em: $shortcutPath"

# Also start now
Start-Process powershell -WindowStyle Hidden -ArgumentList "-File `"$scriptPath`""
Write-Host "[OK] Watchdog iniciado agora."

# Verify
Start-Sleep -Seconds 3
$proc = Get-Process -Name "powershell" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "watchdog_hermes" }
if ($proc) {
    Write-Host "[OK] Watchdog rodando (PID=$($proc.Id))"
} else {
    Write-Host "[AVISO] Watchdog pode estar iniciando..."
}
