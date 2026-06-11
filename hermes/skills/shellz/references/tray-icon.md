# Shellz Tray Icon — Referência de Implementação

## Arquivos do Sistema

| Caminho | Função |
|---------|--------|
| `D:\\projetos\\hermes-watchdog\\shellz_tray.ps1` | Script PowerShell do ícone de bandeja |
| `D:\\projetos\\hermes-watchdog\\shellz_tray.vbs` | Launcher VBS invisível para o PowerShell |
| `D:\\projetos\\hermes-watchdog\\create_tray_shortcuts.ps1` | Cria atalhos Startup + Desktop |
| `%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\ShellzTray.lnk` | Auto-start no login |

## Como o Tray Icon Funciona

O `shellz_tray.ps1` usa `System.Windows.Forms.NotifyIcon` para criar um ícone na bandeja do Windows.

### Ícone dinâmico (3 estados)
```powershell
# Gerado programaticamente com System.Drawing.Bitmap + Graphics
# Verde: Ollama rodando 
# Laranja: Pausado pelo usuário
# Cinza: Ollama não está rodando
$bmp = New-Object System.Drawing.Bitmap(16,16)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.FillEllipse($brush, 1, 1, 14, 14)  # círculo de 14px
$g.DrawString("S", [System.Drawing.Font]::new(...), $brushWhite, 2, 1)
$tray.Icon = [System.Drawing.Icon]::FromHandle($bmp.GetHicon())
```

### Interações
- **Clique esquerdo:** `$tray.Add_Click({ Pause-Ollama })` / `Resume-Ollama`
- **Clique direito:** `$tray.ContextMenuStrip` com 4 itens
- **Balloon notification:** `$tray.ShowBalloonTip(2000, "Shellz", "msg", Info)`
- **Timer:** `$timer.Interval = 10000` atualiza a cada 10s

### Health check
```powershell
function Get-ShellzStatus {
    $ollamaRunning = Get-Process ollama -ErrorAction SilentlyContinue
    $isPaused = Test-Path $env:USERPROFILE\\.shellz_paused
    if ($isPaused) { return "paused" }
    if ($ollamaRunning) { return "running" }
    return "stopped"
}
```

## Auto-Start
- Atalho em `%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\ShellzTray.lnk`
- Caminho: `wscript.exe /B "D:\\projetos\\hermes-watchdog\\shellz_tray.vbs"`
- O VBS executa o PowerShell invisível: `powershell -WindowStyle Hidden -File shellz_tray.ps1`

## Recriação de Atalhos
Se perdidos, execute:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\\projetos\\hermes-watchdog\\create_tray_shortcuts.ps1"
```
