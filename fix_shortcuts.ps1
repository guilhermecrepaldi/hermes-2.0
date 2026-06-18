$wshell = New-Object -ComObject WScript.Shell

# 1. Startup shortcut - Tray Guardian (auto-restart)
$s = $wshell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\ShellzTray.lnk')
$s.TargetPath = 'wscript.exe'
$s.Arguments = '/B "D:\projetos\hermes-watchdog\shellz_tray_guardian.vbs"'
$s.Description = 'Shellz Tray - Pausar/Retomar Ollama (auto-restart)'
$s.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s.WindowStyle = 7
$s.IconLocation = '%SystemRoot%\System32\shell32.dll,14'
$s.Save()
Write-Host "OK: Startup guardian: $($s.FullName)"

# 2. Desktop shortcut - Main Menu
$s2 = $wshell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Shellz Menu.lnk')
$s2.TargetPath = 'cmd.exe'
$s2.Arguments = '/C "D:\projetos\hermes-watchdog\shellz_menu.bat"'
$s2.Description = 'Shellz - Pausar/Retomar Ollama e liberar GPU'
$s2.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s2.WindowStyle = 1
$s2.IconLocation = '%SystemRoot%\System32\shell32.dll,14'
$s2.Save()
Write-Host "OK: Desktop menu: $($s2.FullName)"

# 3. Start Menu shortcut
$s3 = $wshell.CreateShortcut([Environment]::GetFolderPath('Programs') + '\Shellz Menu.lnk')
$s3.TargetPath = 'cmd.exe'
$s3.Arguments = '/C "D:\projetos\hermes-watchdog\shellz_menu.bat"'
$s3.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s3.WindowStyle = 1
$s3.IconLocation = '%SystemRoot%\System32\shell32.dll,14'
$s3.Save()
Write-Host "OK: Start Menu: $($s3.FullName)"

Write-Host ""
Write-Host "=== INSTRUCOES ==="
Write-Host "1. Va ate a area de trabalho"
Write-Host "2. De duplo clique em 'Shellz Menu'"
Write-Host "3. Escolha opcao 5 para abrir o icone na bandeja"
Write-Host ""
Write-Host "Ou clique no 'ShellzTray' na pasta Startup se ja estiver la"
