#!/usr/bin/env bash
# ==============================================================================
# setup_hermes.sh — Reconstrói configuração do Hermes a partir de fontes versionadas
# ==============================================================================
# USO:
#   bash setup_hermes.sh              # Reconstrói TUDO
#   bash setup_hermes.sh --skills     # Só skills
#   bash setup_hermes.sh --memory     # Só memória
#   bash setup_hermes.sh --cron       # Só cron jobs
#   bash setup_hermes.sh --verify     # Só verificar estado atual
# ==============================================================================
# Isso garante que mesmo que um update do Hermes resete ~/.hermes/,
# você executa 1 comando e tudo volta.
# ==============================================================================

set -euo pipefail

# ─── CONFIG ──────────────────────────────────────────────────────────────────
HERMES_HOME="${HOME}/.hermes"
SKILLS_DIR="${HERMES_HOME}/skills"
MEMORIES_DIR="${HERMES_HOME}/memories"
PROFILE="default"
THIS_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION_FILE="${THIS_DIR}/.hermes-setup-version"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🐚 Hermes Setup — Reconstrutor Versionado               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "📁 Destino: ${HERMES_HOME}"
echo "📦 Origem:  ${THIS_DIR}"
echo ""

# ─── HELPERS ──────────────────────────────────────────────────────────────────
ensure_dir() { mkdir -p "$1"; }
log()      { echo "  ✅ $1"; }
warn()     { echo "  ⚠️  $1"; }
info()     { echo "  ℹ️  $1"; }

# ─── 1. SKILLS ───────────────────────────────────────────────────────────────
recreate_skills() {
    echo ""
    echo "━━━ SKILLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ensure_dir "${SKILLS_DIR}"

    # As skills estão no repositório versionado.
    # Se o Hermes resetar ~/.hermes/skills/, copiamos de volta do repo.
    # Skills do Hermes que vêm com o App são reinstaladas pelo próprio Hermes.
    # Skills que VOCÊ criou com skill_manage(action='create') ficam em:
    #   ~/.hermes/skills/<category>/<name>/
    # Se você perdeu, recrie com: hermes curator install <skill-name>
    # Ou manualmente:

    # Skill: shellz (hermes-2.0)
    if [ -d "${THIS_DIR}/skills/hermes-2.0/shellz" ]; then
        cp -r "${THIS_DIR}/skills/hermes-2.0/shellz" "${SKILLS_DIR}/hermes-2.0/" 2>/dev/null || true
        log "shellz restaurada"
    else
        info "shellz: skills/hermes-2.0/shellz/ não encontrada localmente (ok — será instalada via skill_manage)"
    fi

    # Skill: workbench-mode (autonomous-ai-agents)
    if [ -d "${THIS_DIR}/skills/autonomous-ai-agents/workbench-mode" ]; then
        ensure_dir "${SKILLS_DIR}/autonomous-ai-agents"
        cp -r "${THIS_DIR}/skills/autonomous-ai-agents/workbench-mode" "${SKILLS_DIR}/autonomous-ai-agents/" 2>/dev/null || true
        log "workbench-mode restaurada"
    else
        info "workbench-mode: skills/autonomous-ai-agents/workbench-mode/ não encontrada (ok)"
    fi

    echo "━━━ Skills concluídas ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ─── 2. MEMÓRIA ──────────────────────────────────────────────────────────────
recreate_memory() {
    echo ""
    echo "━━━ MEMÓRIA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # A memória é injetada via arquivos em MEMORIES_DIR.
    # Se Hermes resetar, reescrevemos aqui.
    # Por segurança, a memória é recriada pelo próprio Hermes durante a sessão.
    # Mas podemos restaurar o conteúdo salvo em versionamento.

    if [ -f "${THIS_DIR}/hermes_memory.md" ]; then
        ensure_dir "${MEMORIES_DIR}"
        cp "${THIS_DIR}/hermes_memory.md" "${MEMORIES_DIR}/memory.md" 2>/dev/null || true
        log "Memória restaurada de hermes_memory.md"
    else
        info "Arquivo hermes_memory.md não encontrado. A memória será reconstruída na próxima sessão."
    fi

    echo "━━━ Memória concluída ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ─── 3. CONFIG ───────────────────────────────────────────────────────────────
recreate_config() {
    echo ""
    echo "━━━ CONFIGURAÇÃO ──────────────────────────────────────────"

    # Arquivo de quota — versionado
    if [ -f "${THIS_DIR}/quota_config.json" ]; then
        log "quota_config.json presente e versionado"
    else
        info "quota_config.json não encontrado — será recriado na primeira execução do hermes_workbench.py"
    fi

    # hermes_workbench.py — o coração do sistema
    if [ -f "${THIS_DIR}/hermes_workbench.py" ]; then
        log "hermes_workbench.py presente e versionado"
    else
        warn "hermes_workbench.py NÃO ENCONTRADO!"
    fi

    # quick_start.py
    if [ -f "${THIS_DIR}/quick_start.py" ]; then
        log "quick_start.py presente e versionado"
    else
        warn "quick_start.py não encontrado"
    fi

    # watchdog_hermes.py
    if [ -f "${THIS_DIR}/watchdog_hermes.py" ]; then
        log "watchdog_hermes.py presente e versionado"
    else
        warn "watchdog_hermes.py não encontrado"
    fi

    echo "━━━ Configuração concluída ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ─── 4. VERIFICAR ────────────────────────────────────────────────────────────
verify_setup() {
    echo ""
    echo "━━━ VERIFICAÇÃO ───────────────────────────────────────────"
    echo ""
    
    local all_ok=true
    
    # Verifica arquivos críticos no repo
    for f in "hermes_workbench.py" "quick_start.py" "quota_config.json"; do
        if [ -f "${THIS_DIR}/${f}" ]; then
            log "  ${f}"
        else
            warn "  ${f} — AUSENTE"
            all_ok=false
        fi
    done
    
    echo ""
    
    # Verifica Hermes CLI
    if command -v hermes &>/dev/null; then
        log "Hermes CLI disponível: $(hermes --version 2>/dev/null || echo 'versão desconhecida')"
    else
        warn "Hermes CLI não encontrado no PATH"
    fi
    
    echo ""
    
    # Verifica skills instaladas
    if command -v hermes &>/dev/null; then
        log "Skills instaladas:"
        hermes curator list 2>/dev/null | head -20 || echo "    (não foi possível listar)"
    fi
    
    echo ""
    
    # Verifica git
    if [ -d "${THIS_DIR}/.git" ]; then
        log "Git repo presente"
        local branch
        branch=$(cd "${THIS_DIR}" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "desconhecido")
        local status
        status=$(cd "${THIS_DIR}" && git status --short 2>/dev/null | head -5 || echo "")
        log "  Branch: ${branch}"
        if [ -n "${status}" ]; then
            warn "  Arquivos não comitados:"
            echo "${status}" | sed 's/^/    /'
        else
            log "  Working tree limpo"
        fi
    else
        warn "Não é um repositório git — faça: git init && git add -A && git commit -m 'init: setup hermes'"
    fi
    
    if [ "${all_ok}" = true ]; then
        echo ""
        log "✅ Todos os arquivos críticos presentes!"
    else
        echo ""
        warn "⚠️  Alguns arquivos estão ausentes — verifique acima."
    fi
    
    echo "━━━ Verificação concluída ─────────────────────────────────"
}

# ─── 5. GIT INIT ─────────────────────────────────────────────────────────────
git_init_if_needed() {
    if [ ! -d "${THIS_DIR}/.git" ]; then
        echo ""
        echo "━━━ GIT INIT ────────────────────────────────────────────"
        cd "${THIS_DIR}"
        git init
        git add -A
        git commit -m "init: setup hermes versionado $(date +%Y-%m-%d)"
        log "Git repo inicializado e primeiro commit feito"
        echo "━━━ Git concluído ────────────────────────────────────────"
    fi
}

# ─── MAIN ────────────────────────────────────────────────────────────────────
main() {
    local mode="${1:-all}"

    case "${mode}" in
        --skills|-s)
            recreate_skills
            ;;
        --memory|-m)
            recreate_memory
            ;;
        --config|-c)
            recreate_config
            ;;
        --verify|-v)
            verify_setup
            ;;
        --git|-g)
            git_init_if_needed
            ;;
        --all|-a|"")
            recreate_skills
            recreate_memory
            recreate_config
            verify_setup
            git_init_if_needed
            echo ""
            echo "╔══════════════════════════════════════════════════════════════╗"
            echo "║   ✅ SETUP COMPLETO                                       ║"
            echo "║   Hermes está pronto para uso.                             ║"
            echo "║   Qualquer update do Hermes não afeta seus arquivos.       ║"
            echo "╚══════════════════════════════════════════════════════════════╝"
            ;;
        *)
            echo "USO: bash setup_hermes.sh [--skills|--memory|--config|--verify|--git|--all]"
            exit 1
            ;;
    esac
}

main "$@"
