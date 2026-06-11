$startup = [Environment]::GetFolderPath('Startup')
$shortcuts = @(
    @{Name="HermesWatchdog.lnk"; Label="HermesWatchdog"},
    @{Name="HermesShellz_Ollama.lnk"; Label="HermesShellz_Ollama"},
    @{Name="ShellzTray.lnk"; Label="ShellzTray"}
)

foreach ($s in $shortcuts) {
    $path = Join-Path $startup $s.Name
    if (Test-Path $path) {
        $shell = New-Object -ComObject WScript.Shell
        $link = $shell.CreateShortcut($path)
        Write-Host "=== $($s.Label) ==="
        Write-Host "Target: $($link.TargetPath)"
        Write-Host "Args:   $($link.Arguments)"
        Write-Host "Desc:   $($link.Description)"
        Write-Host ""
    } else {
        Write-Host "=== $($s.Label) === NOT FOUND"
        Write-Host ""
    }
}
