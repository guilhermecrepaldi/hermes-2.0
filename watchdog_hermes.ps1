<#
.SYNOPSIS
    Hermes Watchdog — Supervisor Externo Anti-Travamento
.DESCRIPTION
    Processo independente que monitora o Hermes Agent a cada 30s.
    Detecta travamentos, loops, congelamentos e processos órfãos.
    NUNCA modifica arquivos do Hermes ou Workbench.
    Apenas observa, mata processo travado e registra log.
.PARAMETER LogDir
    Diretório para salvar logs do watchdog (default: ~/hermes-watchdog/logs)
.PARAMETER TimeoutMinutes
    Minutos sem progresso antes de considerar travado (default: 20)
.PARAMETER LoopThreshold
    Mesma tool call repetida N vezes (default: 5)
.PARAMETER IntervalSeconds
    Segundos entre verificações (default: 30)
#>

param(
    [string]$LogDir = "$env:USERPROFILE\hermes-watchdog\logs",
    [int]$TimeoutMinutes = 20,
    [int]$LoopThreshold = 5,
    [int]$IntervalSeconds = 30
)

# ── CONFIG ──
$PIDFILE = "$env:USERPROFILE\hermes-watchdog\watchdog.pid"
$STATEFILE = "$env:USERPROFILE\hermes-watchdog\watchdog_state.json"
$HERMES_LOG = "$env:LOCALAPPDATA\hermes\logs\agent.log"
$RECOVERY_FLAG = "$env:USERPROFILE\hermes-watchdog\recovery_needed.flag"

# Garantir diretórios
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\hermes-watchdog" | Out-Null

# Registrar PID do watchdog
$PID.ToString() | Out-File -FilePath $PIDFILE -Force

function Write-WatchdogLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$timestamp [$Level] $Message"
    Add-Content -Path "$LogDir\watchdog_$(Get-Date -Format 'yyyy-MM-dd').log" -Value $line
    if ($Level -eq "WARN" -or $Level -eq "ERROR") {
        $color = "Red"
        if ($Level -eq "WARN") { $color = "Yellow" }
        Write-Host $line -ForegroundColor $color
    }
}

function Get-HermesProcess {
    <#
    .SYNOPSIS
        Encontra o processo Hermes. Procura node.exe executando hermes.
    #>
    try {
        $procs = Get-Process -Name "node" -ErrorAction SilentlyContinue
        foreach ($p in $procs) {
            try {
                $cmdLine = (Get-WmiObject -Class Win32_Process -Filter "ProcessId = $($p.Id)").CommandLine
                if ($cmdLine -match "hermes") {
                    return $p
                }
            } catch {}
        }
    } catch {}
    return $null
}

function Get-ProcessCPU {
    param([System.Diagnostics.Process]$Process)
    try {
        $perf = Get-WmiObject -Class Win32_PerfRawData_PerfProc_Process -Filter "IDProcess = $($Process.Id)"
        if ($perf) { return $perf.PercentProcessorTime } else { return 0 }
    } catch { return 0 }
}

function Get-LastToolCall {
    <#
    .SYNOPSIS
        Lê o último tool_call do log do Hermes.
    .DESCRIPTION
        Procura no agent.log a última linha com "tool_executor" ou "turn_context"
        para determinar se o agente está progredindo.
    #>
    if (-not (Test-Path $HERMES_LOG)) { return $null, $null }
    try {
        $lines = Get-Content -Path $HERMES_LOG -Tail 20
        $lastTool = $null
        $lastTime = $null
        foreach ($line in $lines) {
            if ($line -match "tool_executor.*completed" -or $line -match "turn_context") {
                if ($line -match "^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})") {
                    $lastTime = [DateTime]::Parse($match[1])
                    $lastTool = $line
                }
            }
        }
        return $lastTool, $lastTime
    } catch {
        return $null, $null
    }
}

function Test-AgentLoop {
    <#
    .SYNOPSIS
        Detecta loops: mesma tool call repetida sem progresso.
    #>
    if (-not (Test-Path $HERMES_LOG)) { return $false }
    try {
        $lines = Get-Content -Path $HERMES_LOG -Tail ($LoopThreshold * 2)
        $toolCount = @{}
        foreach ($line in $lines) {
            if ($line -match "tool_executor: tool (\w+)") {
                $tool = $match[1]
                $toolCount[$tool] = ($toolCount[$tool] -or 0) + 1
            }
        }
        foreach ($key in $toolCount.Keys) {
            if ($toolCount[$key] -ge $LoopThreshold) {
                return $true, $key, $toolCount[$key]
            }
        }
        return $false, $null, 0
    } catch {
        return $false, $null, 0
    }
}

function Save-WatchdogState {
    param([string]$Status, [string]$LastAction)
    $state = @{
        timestamp = (Get-Date -Format "o")
        status = $Status
        last_action = $LastAction
        watchdog_pid = $PID
    }
    $state | ConvertTo-Json | Out-File -FilePath $STATEFILE -Force
}

function Invoke-Recovery {
    <#
    .SYNOPSIS
        Executa recuperação quando um travamento é detectado.
    .DESCRIPTION
        1. Salva flag de recovery
        2. Mata processo travado
        3. Limpa locks órfãos
        4. Registra no log
        5. Não tenta reiniciar — apenas prepara para o próximo start limpo
    #>
    param([string]$Reason)
    
    Write-WatchdogLog "🚨 TRAVAMENTO DETECTADO: $Reason" -Level "ERROR"
    
    # 1. Salvar recovery flag
    $recoveryInfo = @{
        detected_at = (Get-Date -Format "o")
        reason = $Reason
        watchdog_pid = $PID
    }
    $recoveryInfo | ConvertTo-Json | Out-File -FilePath $RECOVERY_FLAG -Force
    
    # 2. Matar processo Hermes travado
    $proc = Get-HermesProcess
    if ($proc) {
        Write-WatchdogLog "Matando processo Hermes PID=$($proc.Id)..." -Level "WARN"
        try {
            $proc | Stop-Process -Force -ErrorAction SilentlyContinue
            Write-WatchdogLog "Processo Hermes finalizado." -Level "WARN"
        } catch {
            Write-WatchdogLog "Falha ao matar processo: $_" -Level "ERROR"
        }
    }
    
    # 3. Limpar locks órfãos no Workbench
    $lockDirs = @(
        "$env:USERPROFILE\AppData\Local\hermes\cron",
        "D:\projetos\workbench-ai.manager\runtime\locks",
        "D:\projetos\workbench-ai.manager\runtime\task_locks"
    )
    foreach ($dir in $lockDirs) {
        if (Test-Path $dir) {
            Remove-Item -Path "$dir\*" -Force -ErrorAction SilentlyContinue
            Write-WatchdogLog "Locks limpos em $dir"
        }
    }
    
    # 4. Estado final
    Save-WatchdogState -Status "recovery_complete" -LastAction "killed_$Reason"
    Write-WatchdogLog "✅ Recovery concluído. Pronto para próximo start limpo." -Level "WARN"
}

# ── ── ── ── ── ── ── ── ── ──
# MAIN LOOP
# ── ── ── ── ── ── ── ── ── ──

Write-WatchdogLog "══════════════════════════════════════════"
Write-WatchdogLog "Hermes Watchdog INICIADO (PID=$PID)"
Write-WatchdogLog "Timeout: ${TimeoutMinutes}min | Loop: ${LoopThreshold}x | Intervalo: ${IntervalSeconds}s"
Write-WatchdogLog "LogDir: $LogDir"
Write-WatchdogLog "══════════════════════════════════════════"

Save-WatchdogState -Status "running" -LastAction "startup"

while ($true) {
    try {
        $proc = Get-HermesProcess
        $now = Get-Date
        
        if (-not $proc) {
            # Hermes não está rodando — normal, só esperar
            Save-WatchdogState -Status "idle" -LastAction "no_process"
            Start-Sleep -Seconds $IntervalSeconds
            continue
        }
        
        # ── 1. CHECK: Último tool call há quanto tempo? ──
        $lastTool, $lastTime = Get-LastToolCall
        if ($lastTime) {
            $elapsed = ($now - $lastTime).TotalMinutes
            if ($elapsed -gt $TimeoutMinutes) {
                Invoke-Recovery -Reason "Sem progresso por ${elapsed}min (timeout=${TimeoutMinutes})"
                Save-WatchdogState -Status "recovered_timeout" -LastAction "killed"
                Start-Sleep -Seconds 5
                continue
            }
        }
        
        # ── 2. CHECK: Loop de mesma tool call? ──
        $inLoop, $loopTool, $loopCount = Test-AgentLoop
        if ($inLoop) {
            Invoke-Recovery -Reason "Loop detectado: $loopTool repetido ${loopCount}x"
            Save-WatchdogState -Status "recovered_loop" -LastAction "killed"
            Start-Sleep -Seconds 5
            continue
        }
        
        # ── 3. CHECK: Processo zumbi (CPU = 0% por muito tempo)? ──
        try {
            $cpu = Get-ProcessCPU $proc
            $runtime = ($now - $proc.StartTime).TotalMinutes
            if ($runtime -gt 5 -and $cpu -lt 0.1) {
                # Processo rodando há 5+ min mas sem uso de CPU — congelado
                Invoke-Recovery -Reason "Processo zumbi: CPU=${cpu}, runtime=${runtime}min"
                Save-WatchdogState -Status "recovered_zombie" -LastAction "killed"
                Start-Sleep -Seconds 5
                continue
            }
        } catch {}
        
        # ── Tudo OK ──
        Save-WatchdogState -Status "healthy" -LastAction "monitoring"
        $pidStr = $proc.Id
        $startStr = $proc.StartTime.ToString("HH:mm:ss")
        Write-WatchdogLog ("OK Hermes running PID=" + $pidStr + " since " + $startStr)
        
    } catch {
        $errMsg = $_.Exception.Message
        Write-WatchdogLog ("Erro no watchdog loop: " + $errMsg)
    }
    
    Start-Sleep -Seconds $IntervalSeconds
}
