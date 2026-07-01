# 🏠 Setup Neo Hermes — PC Novo / Formatação
# Execute no PowerShell como Administrador OU no git-bash

Write-Host "🏠 Setup Neo Hermes - PC Novo" -ForegroundColor Cyan
Write-Host "========================================"

# 1. Verificar requisitos
Write-Host "`n[1/7] Verificando requisitos..." -ForegroundColor Yellow
$reqs = @(
    @{Name="Git"; Check="git --version"},
    @{Name="Python"; Check="python --version"},
    @{Name="Node.js"; Check="node --version"},
    @{Name="gh CLI"; Check="gh --version"}
)
foreach ($r in $reqs) {
    $ok = !(Invoke-Expression $r.Check 2>$null)
    if ($ok) { Write-Host "  ✅ $($r.Name)" -ForegroundColor Green }
    else { Write-Host "  ❌ $($r.Name) — Instalar manualmente" -ForegroundColor Red }
}

# 2. Clonar neo-hermes
Write-Host "`n[2/7] Clonando neo-hermes..." -ForegroundColor Yellow
$repo = "$env:USERPROFILE\neo-hermes"
if (Test-Path "$repo\.git") {
    Write-Host "  ✅ Repo ja existe" -ForegroundColor Green
} else {
    git clone https://github.com/guilhermecrepaldi/neo-hermes.git $repo
    Write-Host "  ✅ Clonado" -ForegroundColor Green
}

# 3. Instalar Ollama
Write-Host "`n[3/7] Verificando Ollama..." -ForegroundColor Yellow
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "  ✅ Ollama $(ollama --version)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Baixe em: https://ollama.com/download" -ForegroundColor Yellow
}

# 4. Pull modelo S1
Write-Host "`n[4/7] Baixando modelo S1..." -ForegroundColor Yellow
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    $hasModel = ollama list | Select-String "qwen2.5-coder:7b"
    if ($hasModel) {
        Write-Host "  ✅ qwen2.5-coder:7b ja existe" -ForegroundColor Green
    } else {
        ollama pull qwen2.5-coder:7b
        Write-Host "  ✅ qwen2.5-coder:7b baixado" -ForegroundColor Green
    }
}

# 5. Copiar scripts Startup
Write-Host "`n[5/7] Configurando auto-start..." -ForegroundColor Yellow
$startup = [Environment]::GetFolderPath('Startup')
Copy-Item "$repo\watchdog\start_ambiente.bat" "$startup\" -Force
Copy-Item "$repo\watchdog\ollama_invisible.vbs" "$startup\hermes_ollama.vbs" -Force
Write-Host "  ✅ Scripts copiados pra Startup" -ForegroundColor Green

# 6. Instalar dependências Python
Write-Host "`n[6/7] Instalando dependencias..." -ForegroundColor Yellow
pip install feedparser yt-dlp requests pyyaml rich Pillow 2>&1 | Out-Null
Write-Host "  ✅ Dependencias instaladas" -ForegroundColor Green

# 7. Configurar Hermes
Write-Host "`n[7/7] Configurando Hermes..." -ForegroundColor Yellow
hermes config set model.default deepseek-v4-flash
hermes config set model.provider deepseek
hermes config set autoload_skills "caveman-hermes,agent-reach,shellz-environment"
Write-Host "  ✅ Hermes configurado!" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🏠 SETUP COMPLETO!" -ForegroundColor Green
Write-Host "========================================"
Write-Host "Proximo passo:"
Write-Host "  1. Instalar Agent Reach: pip install https://github.com/Panniantong/agent-reach/archive/main.zip"
Write-Host "  2. Instalar OpenCLI: npm install -g @jackwener/opencli"
Write-Host "  3. Ver: $repo\AMBIENTE.md"
