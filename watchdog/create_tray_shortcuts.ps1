$wshell = New-Object -ComObject WScript.Shell

# Startup shortcut
$s = $wshell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\ShellzTray.lnk')
$s.TargetPath = 'wscript.exe'
$s.Arguments = '/B "D:\projetos\hermes-watchdog\shellz_tray.vbs"'
$s.Description = 'Shellz Tray - Pausar/Retomar Ollama'
$s.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s.WindowStyle = 7
$s.IconLocation = '%SystemRoot%\System32\shell32.dll,14'
$s.Save()
Write-Host "Startup: $($s.FullName)"

# Desktop shortcut
$s2 = $wshell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\🐚 Shellz Tray.lnk')
$s2.TargetPath = 'wscript.exe'
$s2.Arguments = '/B "D:\projetos\hermes-watchdog\shellz_tray.vbs"'
$s2.Description = 'Shellz Tray - Pausar/Retomar Ollama'
$s2.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s2.WindowStyle = 7
$s2.IconLocation = '%SystemRoot%\System32\shell32.dll,14'
$s2.Save()
Write-Host "Desktop: $($s2.FullName)"
