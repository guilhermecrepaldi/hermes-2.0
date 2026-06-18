# Cria atalho do Hermes Watchdog na pasta Startup

$wshell = New-Object -ComObject WScript.Shell
$startup = [Environment]::GetFolderPath('Startup')
$target = "cmd.exe"
$args = '/C start /B /MIN "HermesWatchdog" D:\projetos\hermes-watchdog\watchdog_hermes.bat'
$shortcutPath = Join-Path $startup "HermesWatchdog.lnk"

$shortcut = $wshell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $target
$shortcut.Arguments = $args
$shortcut.Description = "Hermes Watchdog 24/7 - Anti-Travamento"
$shortcut.WorkingDirectory = "D:\projetos\hermes-watchdog"
$shortcut.WindowStyle = 7  # Minimized
$shortcut.Save()

Write-Host "OK - Atalho criado: $shortcutPath"
