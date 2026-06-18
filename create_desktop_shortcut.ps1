$wshell = New-Object -ComObject WScript.Shell

# Desktop shortcut - Shellz Menu
$s = $wshell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Shellz Menu.lnk')
$s.TargetPath = 'cmd.exe'
$s.Arguments = '/C "D:\projetos\hermes-watchdog\shellz_menu.bat"'
$s.Description = 'Shellz - Pausar/Retomar Ollama e liberar GPU'
$s.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s.WindowStyle = 1  # Normal window
$s.IconLocation = '%SystemRoot%\System32\shell32.dll,14'
$s.Save()
Write-Host "OK: Desktop shortcut created: $($s.FullName)"

# Also create one in Start Menu
$startMenu = [Environment]::GetFolderPath('Programs')
$s2 = $wshell.CreateShortcut("$startMenu\Shellz Menu.lnk")
$s2.TargetPath = 'cmd.exe'
$s2.Arguments = '/C "D:\projetos\hermes-watchdog\shellz_menu.bat"'
$s2.Description = 'Shellz - Pausar/Retomar Ollama e liberar GPU'
$s2.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s2.WindowStyle = 1
$s2.IconLocation = '%SystemRoot%\System32\shell32.dll,14'
$s2.Save()
Write-Host "OK: Start Menu shortcut created: $($s2.FullName)"

# Also verify the tray shortcut exists
$trayShortcut = [Environment]::GetFolderPath('Startup') + '\ShellzTray.lnk'
if (Test-Path $trayShortcut) {
    Write-Host "OK: Tray startup shortcut exists"
} else {
    Write-Host "WARN: Tray startup shortcut missing - recreating..."
    $s3 = $wshell.CreateShortcut($trayShortcut)
    $s3.TargetPath = 'wscript.exe'
    $s3.Arguments = '/B "D:\projetos\hermes-watchdog\shellz_tray.vbs"'
    $s3.WorkingDirectory = 'D:\projetos\hermes-watchdog'
    $s3.WindowStyle = 7
    $s3.IconLocation = '%SystemRoot%\System32\shell32.dll,14'
    $s3.Save()
    Write-Host "OK: Recreated"
}
