$wshell = New-Object -ComObject WScript.Shell
$s = $wshell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\HermesShellz_Ollama.lnk')
$s.TargetPath = 'wscript.exe'
$s.Arguments = '/B "D:\projetos\hermes-watchdog\ollama_invisible.vbs"'
$s.Description = 'Hermes Shellz - Ollama Server (Invisivel)'
$s.WorkingDirectory = 'D:\projetos\hermes-watchdog'
$s.WindowStyle = 7
$s.IconLocation = '%SystemRoot%\System32\wbem\wmiprvse.exe,0'
$s.Save()
Write-Host "Startup shortcut criado: $($s.FullName)"
