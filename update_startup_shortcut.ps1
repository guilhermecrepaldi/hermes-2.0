$wshell = New-Object -ComObject WScript.Shell
$s = $wshell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\HermesWatchdog.lnk')
$s.TargetPath = 'wscript.exe'
$s.Arguments = '/B "D:\projetos\hermes-watchdog\watchdog_invisible.vbs"'
$s.Description = 'Hermes 2.0 - Watchdog 24/7 (Zero Janelas)'
$s.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s.WindowStyle = 7
$s.Save()
Write-Host "OK: HermesWatchdog shortcut updated"
