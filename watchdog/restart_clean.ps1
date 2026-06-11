Write-Host "=== MATANDO TODOS OS WSCRIPT (watchdogs antigos) ==="
Get-Process wscript -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "OK: wscripts mortos"

Write-Host ""
Write-Host "=== MATANDO TODOS OS PYTHONW (watchdogs antigos) ==="
Get-Process pythonw -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "OK: pythonws mortos"

Write-Host ""
Write-Host "=== MATANDO CMDS COM TITULO HermesWatchdog ==="
Get-Process cmd | Where-Object { $_.MainWindowTitle -match "HermesWatchdog|watchdog|shellz" } | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "OK"

Write-Host ""
Write-Host "=== INICIANDO WATCHDOG NOVO (pythonw, zero janelas) ==="
Start-Process wscript.exe -ArgumentList '/B "D:\projetos\hermes-watchdog\watchdog_invisible.vbs"' -WindowStyle Hidden
Write-Host "OK: Watchdog guardian iniciado"

Write-Host ""
Write-Host "=== INICIANDO SHELLZ TRAY ==="
Start-Process wscript.exe -ArgumentList '/B "D:\projetos\hermes-watchdog\shellz_tray_guardian.vbs"' -WindowStyle Hidden
Write-Host "OK: Shellz Tray guardian iniciado"

Write-Host ""
Write-Host "=== VERIFICANDO ==="
Start-Sleep -Seconds 2
$ws = Get-Process wscript -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count
$pw = Get-Process pythonw -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count
$ol = Get-Process ollama -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "wscript.exe: $ws processos"
Write-Host "pythonw.exe: $pw processos"
Write-Host "ollama.exe: $ol processos"

Write-Host ""
Write-Host "=== VERIFICANDO JANELAS CMD VISIVEIS ==="
$visible = Get-Process cmd | Where-Object { $_.MainWindowTitle -ne "" -and $_.MainWindowTitle -match "HermesWatchdog|watchdog" }
if ($visible) {
    Write-Host "ATENCAO: Ainda existem janelas cmd visiveis!"
    $visible | Format-Table Id, MainWindowTitle
} else {
    Write-Host "ZERO janelas cmd com titulo HermesWatchdog"
}
