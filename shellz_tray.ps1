Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# ─── CONFIG ───
$ScriptDir = "D:\projetos\hermes-watchdog"
$PauseFlag = "$env:USERPROFILE\.shellz_paused"
$OllamaExe = "C:\Users\Home\AppData\Local\Programs\Ollama\ollama.exe"

# ─── TRAY ICON ───
$tray = New-Object System.Windows.Forms.NotifyIcon
$tray.Text = "🐚 Shellz — Ollama Rodando"
$tray.Visible = $true

# Create a simple icon programmatically (green circle)
$bmp = New-Object System.Drawing.Bitmap(16,16)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'
$brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    (New-Object System.Drawing.Point(0,0)),
    (New-Object System.Drawing.Point(16,16)),
    [System.Drawing.Color]::LimeGreen,
    [System.Drawing.Color]::DarkGreen
)
$g.FillEllipse($brush, 1, 1, 14, 14)
$g.DrawString("S", [System.Drawing.Font]::new('Segoe UI',10,[System.Drawing.FontStyle]::Bold),
    [System.Drawing.Brushes]::White, 2, 1)
$g.Dispose()
$icon = [System.Drawing.Icon]::FromHandle($bmp.GetHicon())
$tray.Icon = $icon

# ─── STATUS CHECK ───
function Get-ShellzStatus {
    $ollamaRunning = Get-Process ollama -ErrorAction SilentlyContinue
    $isPaused = Test-Path $PauseFlag
    if ($isPaused) { return "paused" }
    if ($ollamaRunning) { return "running" }
    return "stopped"
}

function Update-Tray {
    $status = Get-ShellzStatus
    switch ($status) {
        "running" { 
            $tray.Text = "🐚 Shellz — Ollama Rodando"
            $brush = [System.Drawing.Drawing2D.LinearGradientBrush]::new(
                (New-Object System.Drawing.Point(0,0)),
                (New-Object System.Drawing.Point(16,16)),
                [System.Drawing.Color]::LimeGreen,
                [System.Drawing.Color]::DarkGreen
            )
        }
        "paused" { 
            $tray.Text = "⏸ Shellz — Pausado (GPU livre)"
            $brush = [System.Drawing.Drawing2D.LinearGradientBrush]::new(
                (New-Object System.Drawing.Point(0,0)),
                (New-Object System.Drawing.Point(16,16)),
                [System.Drawing.Color]::Orange,
                [System.Drawing.Color]::DarkOrange
            )
        }
        "stopped" { 
            $tray.Text = "⛔ Shellz — Ollama Parado"
            $brush = [System.Drawing.Drawing2D.LinearGradientBrush]::new(
                (New-Object System.Drawing.Point(0,0)),
                (New-Object System.Drawing.Point(16,16)),
                [System.Drawing.Color]::Gray,
                [System.Drawing.Color]::DarkGray
            )
        }
    }
    $g2 = [System.Drawing.Graphics]::FromImage($bmp)
    $g2.SmoothingMode = 'AntiAlias'
    $g2.Clear([System.Drawing.Color]::Transparent)
    $g2.FillEllipse($brush, 1, 1, 14, 14)
    $g2.DrawString("S", [System.Drawing.Font]::new('Segoe UI',10,[System.Drawing.FontStyle]::Bold),
        [System.Drawing.Brushes]::White, 2, 1)
    $g2.Dispose()
    $oldIcon = $tray.Icon
    $tray.Icon = [System.Drawing.Icon]::FromHandle($bmp.GetHicon())
    if ($oldIcon) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($oldIcon.Handle) | Out-Null }
    $brush.Dispose()
}

# ─── ACTIONS ───
function Pause-Ollama {
    Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
    Set-Content -Path $PauseFlag -Value "paused by user $(Get-Date)" -Force
    Update-Tray
    $tray.ShowBalloonTip(2000, "🐚 Shellz", "Ollama pausado. GPU livre para jogos!", [System.Windows.Forms.ToolTipIcon]::Info)
}

function Resume-Ollama {
    if (-not (Get-Process ollama -ErrorAction SilentlyContinue)) {
        Start-Process -FilePath "wscript.exe" -ArgumentList "/B `"$ScriptDir\ollama_invisible.vbs`"" -WindowStyle Hidden
        Start-Sleep -Seconds 3
    }
    if (Test-Path $PauseFlag) { Remove-Item $PauseFlag -Force }
    Update-Tray
    $tray.ShowBalloonTip(2000, "🐚 Shellz", "Ollama retomado. Shell 1 ativo!", [System.Windows.Forms.ToolTipIcon]::Info)
}

# ─── CLICK HANDLERS ───
$tray.Add_Click({
    # Left click = toggle pause/resume
    $status = Get-ShellzStatus
    if ($status -eq "running") { Pause-Ollama }
    elseif ($status -eq "paused") { Resume-Ollama }
})

# ─── RIGHT-CLICK MENU ───
$menu = New-Object System.Windows.Forms.ContextMenuStrip

$itemPause = New-Object System.Windows.Forms.ToolStripMenuItem
$itemPause.Text = "⏸ Pausar Ollama (liberar GPU)"
$itemPause.Add_Click({ Pause-Ollama })

$itemResume = New-Object System.Windows.Forms.ToolStripMenuItem
$itemResume.Text = "▶ Retomar Ollama"
$itemResume.Add_Click({ Resume-Ollama })

$itemStatus = New-Object System.Windows.Forms.ToolStripMenuItem
$itemStatus.Text = "📊 Ver Status"
$itemStatus.Add_Click({
    $status = Get-ShellzStatus
    switch ($status) {
        "running" { $msg = "🐚 Shell 1 (Ollama): ✅ Rodando`nGPU: Ativa`nModelo: qwen2.5-coder:7b" }
        "paused"  { $msg = "🐚 Shell 1 (Ollama): ⏸ Pausado`nGPU: Livre para jogos`nClique em Retomar para reativar" }
        "stopped" { $msg = "🐚 Shell 1 (Ollama): ⛔ Parado`nClique em Retomar para iniciar" }
    }
    [System.Windows.Forms.MessageBox]::Show($msg, "Shellz Status", "OK", "Information")
})

$itemExit = New-Object System.Windows.Forms.ToolStripMenuItem
$itemExit.Text = "❌ Sair"
$itemExit.Add_Click({
    $tray.Visible = $false
    $tray.Dispose()
    [System.Windows.Forms.Application]::Exit()
})

$menu.Items.Add($itemPause) | Out-Null
$menu.Items.Add($itemResume) | Out-Null
$menu.Items.Add("-") | Out-Null  # separator
$menu.Items.Add($itemStatus) | Out-Null
$menu.Items.Add("-") | Out-Null
$menu.Items.Add($itemExit) | Out-Null

$tray.ContextMenuStrip = $menu

# ─── AUTO-START OLLAMA IF NOT RUNNING ───
$status = Get-ShellzStatus
if ($status -eq "stopped") {
    Start-Process -FilePath "wscript.exe" -ArgumentList "/B `"$ScriptDir\ollama_invisible.vbs`"" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Update-Tray
}

# ─── TIMER (update every 10s) ───
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 10000
$timer.Add_Tick({ Update-Tray })
$timer.Start()

# ─── RUN ───
[System.Windows.Forms.Application]::Run()
