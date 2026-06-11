$wshell = New-Object -ComObject WScript.Shell

# Pausar shortcut
$s = $wshell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\🐚 Shellz Pausar.lnk')
$s.TargetPath = 'cmd.exe'
$s.Arguments = '/C "D:\projetos\hermes-watchdog\shellz_pausar.bat"'
$s.Description = 'Pausar Ollama e liberar GPU para jogos'
$s.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s.WindowStyle = 1
$s.IconLocation = '%SystemRoot%\System32\shell32.dll,14'
$s.Save()
Write-Host "Atalho PAUSAR criado na Desktop"

# Retomar shortcut
$s2 = $wshell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\🐚 Shellz Retomar.lnk')
$s2.TargetPath = 'cmd.exe'
$s2.Arguments = '/C "D:\projetos\hermes-watchdog\shellz_retomar.bat"'
$s2.Description = 'Retomar Ollama e reativar Shell 1'
$s2.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s2.WindowStyle = 1
$s2.IconLocation = '%SystemRoot%\System32\shell32.dll,27'
$s2.Save()
Write-Host "Atalho RETOMAR criado na Desktop"
