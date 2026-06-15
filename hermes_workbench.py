#!/usr/bin/env python3
"""
Hermes Workbench — CLI Unificada
Usa detecção automática de quota + LLM inteligente baseado em rankings IA

Comandos Base:
  intelligence-router <complexidade> <tokens>  Seleciona LLM ideal baseado em inteligência Artificial Analysis
  help                                           Mostra ajuda
  status                                         Mostra status do sistema
"""

import sys
import json
from datetime import datetime

# Inteligência baseada nos rankings da Artificial Analysis (mais alto é melhor)
LLM_INTELLIGENCE_RANKS = {
    'claude-fable-5': {'intelligence': 65, 'speed': 64, 'provider': 'anthropic', 'priority': 1, 'max_tokens': 8192},
    'gpt-5.5-xhigh': {'intelligence': 60, 'speed': 64, 'provider': 'openai', 'priority': 2, 'max_tokens': 8192},
    'gemini-3.1-pro': {'intelligence': 57, 'speed': 64, 'provider': 'google', 'priority': 3, 'max_tokens': 8192},
    'grok-4.3-high': {'intelligence': 53, 'speed': 64, 'provider': 'xai', 'priority': 4, 'max_tokens': 6144},
    'deepseek-v4-pro': {'intelligence': 52, 'speed': 64, 'provider': 'deepseek', 'priority': 5, 'max_tokens': 6144},
    'claude-opus-4.8': {'intelligence': 48, 'speed': 48, 'provider': 'anthropic', 'priority': 6, 'max_tokens': 4096},
    'gpt-5-codex': {'intelligence': 46, 'speed': 45, 'provider': 'openai', 'priority': 7, 'max_tokens': 4096},
}

# Modelos locais gratuitos (S1 - Ollama)
LOCAL_MODELS = {
    'qwen2.5-coder:7b': {'intelligence': 35, 'speed': 30, 'provider': 'ollama', 'priority': 10, 'max_tokens': 4096, 'cost': 0},
    'deepseek-coder:6.7b': {'intelligence': 38, 'speed': 28, 'provider': 'ollama', 'priority': 9, 'max_tokens': 4096, 'cost': 0},
    'llama3.1:8b': {'intelligence': 32, 'speed': 35, 'provider': 'ollama', 'priority': 11, 'max_tokens': 4096, 'cost': 0},
}

def get_optimal_llm_for_task(task_complexity, token_quota_remaining, prefer_local=True):
    """
    Seleciona o LLM ideal baseado em:
    1. Inteligência (principal critério) - Artificial Analysis rankings
    2. Tokens restantes - se quota acabando, cai no ranking
    3. Tipo de tarefa - S3 para tarefas complexas, S2 para médias, S1 para simples
    4. Preferência por modelos locais gratuitos quando possível

    Retorna: (modelo, provider, tokens_estimados, specs)
    """
    # Calcula tokens necessários baseado na complexidade
    if task_complexity >= 8:  # Muito complexo
        required_tokens = min(12000, token_quota_remaining)
        min_intelligence = 50
    elif task_complexity >= 6:  # Complexo
        required_tokens = min(8000, token_quota_remaining)
        min_intelligence = 45
    elif task_complexity >= 4:  # Médio
        required_tokens = min(4000, token_quota_remaining)
        min_intelligence = 35
    else:  # Simples
        required_tokens = min(2000, token_quota_remaining)
        min_intelligence = 25

    # Se tokens muito baixos ou tarefa simples com preferência local, usa modelos locais S1
    use_local_now = False
    if token_quota_remaining < 500:
        use_local_now = True
    elif prefer_local and task_complexity <= 5:
        # Tarefas simples/médias (complexidade 1-5) vão para modelos locais
        use_local_now = True
    elif prefer_local and token_quota_remaining < 2000:
        use_local_now = True
    
    if use_local_now:
        if prefer_local:
            best_local = max(LOCAL_MODELS.items(), key=lambda x: x[1]['intelligence'])
            return (best_local[0], 'ollama', min(required_tokens, token_quota_remaining, 4096), best_local[1])
        return ('llama2', 'ollama', min(required_tokens, token_quota_remaining, 4096), {'intelligence': 30, 'speed': 25, 'provider': 'ollama', 'priority': 12, 'max_tokens': 4096})

    # Decide pool de modelos: se tarefa simples/média e prefere local, tenta local primeiro
    all_models = dict(LLM_INTELLIGENCE_RANKS)
    if prefer_local and task_complexity <= 6:
        all_models.update(LOCAL_MODELS)

    # Filtra LLMs que podem acomodar a tarefa
    candidates = []
    for model_name, specs in all_models.items():
        if required_tokens <= specs['max_tokens'] and specs['intelligence'] >= min_intelligence:
            candidates.append((specs['priority'], model_name, specs['provider'], specs['intelligence'], specs['speed'], specs['max_tokens']))

    # Se nenhum LLM pode acomodar a tarefa, usa o melhor disponível
    if not candidates:
        all_candidates = [(s['priority'], n, s['provider'], s['intelligence'], s['speed'], s['max_tokens']) 
                          for n, s in all_models.items()]
        all_candidates.sort(key=lambda x: (x[3], x[4]), reverse=True)
        best = all_candidates[0]
        return (best[1], best[2], min(best[5], token_quota_remaining), {
            'intelligence': best[3], 'speed': best[4], 'provider': best[2], 'priority': best[0], 'max_tokens': best[5]
        })

    # Ordena por inteligência e velocidade (maior primeiro)
    candidates.sort(key=lambda x: (-x[3], -x[4]))

    # Se tokens restantes < 25% de requisito, cai um nível no ranking
    if token_quota_remaining < (required_tokens * 0.25):
        current_priority = candidates[0][0]
        fallback_candidates = [c for c in candidates if c[0] > current_priority]
        if fallback_candidates:
            best = min(fallback_candidates, key=lambda x: x[0])
        else:
            best = candidates[0]
    else:
        best = candidates[0]

    model_name, provider, intelligence, speed, max_tokens = best[1], best[2], best[3], best[4], best[5]
    actual_tokens = min(max_tokens, token_quota_remaining)

    return (model_name, provider, actual_tokens, {
        'intelligence': intelligence, 'speed': speed, 'provider': provider, 
        'priority': best[0], 'max_tokens': max_tokens
    })


def cmd_intelligence_based_router(args):
    """
    Router baseado em inteligência Artificial Analysis.
    Seleciona automaticamente o LLM ideal baseado em:
    - Complexidade da tarefa
    - Tokens restantes
    - Ranking de inteligência
    """
    if not args:
        print("Uso: hermes-workbench intelligence-router <complexidade> <tokens_restantes> [--cloud-only]")
        print("Complexidade: 1-10 (1=simples, 10=muito complexo)")
        print("  --cloud-only: força uso de modelos cloud (sem Ollama)")
        return 1

    prefer_local = '--cloud-only' not in args
    clean_args = [a for a in args if a != '--cloud-only']

    try:
        task_complexity = int(clean_args[0])
        token_quota_remaining = int(clean_args[1]) if len(clean_args) > 1 else 10000
    except ValueError:
        print("Erro: Parametros inválidos. Use: hermes-workbench intelligence-router <complexidade> <tokens_restantes> [--cloud-only]")
        return 1

    if not (1 <= task_complexity <= 10):
        print("Erro: Complexidade deve estar entre 1 e 10")
        return 1
    if token_quota_remaining <= 0:
        print("Erro: Tokens restantes devem ser positivos")
        return 1

    # Seleciona LLM ideal
    model_name, provider, tokens_to_use, model_info = get_optimal_llm_for_task(
        task_complexity, token_quota_remaining, prefer_local
    )

    intelligence = model_info['intelligence']
    speed = model_info['speed']
    max_tokens = model_info['max_tokens']
    is_local = provider == 'ollama'

    print(f"🧠 Roteamento Inteligente Baseado em AI Analysis")
    print(f"📊 Tarefa: Complexidade {task_complexity}/10, Tokens restantes {token_quota_remaining:,}")
    print(f"🏆 Modelo Selecionado: {model_name} ({provider}) {'🆓 LOCAL' if is_local else '☁️ CLOUD'}")
    print(f"📈 Inteligência: {intelligence}/100 (Rank {model_info['priority']})")
    print(f"⚡ Speed: {speed} tokens/segundo")
    print(f"💾 Tokens a Usar: {tokens_to_use:,}/{max_tokens:,}")
    print(f"💰 Custo: {'GRATUITO' if is_local else f'~${0.15 if intelligence < 50 else 0.50}/M tokens'}")

    # Mostra se está no limite de quota
    if token_quota_remaining < (tokens_to_use * 0.5):
        print(f"⚠️  BAIXO TOKEN ALERT: Apenas {token_quota_remaining:,} restantes")
        print(f"   Considere usar tarefa de menor complexidade ou recarregar quota")

    return 0


def cmd_help(args):
    """Mostra ajuda."""
    print(__doc__)
    print("\nExemplos:")
    print('  hermes-workbench intelligence-router 8 5000        # Tarefa complexa com 5k tokens')
    print('  hermes-workbench intelligence-router 4 500         # Tarefa média com poucos tokens')
    print('  hermes-workbench intelligence-router 2 50 --cloud-only  # Tarefa simples, força cloud')
    print('  hermes-workbench help                              # Esta ajuda')
    return 0


def cmd_status(args):
    """Mostra status do sistema Hermes."""
    print("🤖 Hermes 3.1 Workbench — Status")
    print("=" * 60)
    print(f"📅 Verificado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔄 Modelos Cloud Disponíveis: {len(LLM_INTELLIGENCE_RANKS)}")
    print(f"🏠 Modelos Locais (Ollama): {len(LOCAL_MODELS)}")
    print(f"💰 Quota estimada: Baseada em tokens restantes")
    print(f"📊 Eficiência alvo: 85%+ uso de quota")
    return 0


def cmd_s1_router(args):
    """Router S1/S2/S3 baseado em palavras-chave da tarefa."""
    if not args:
        task = input("Descreva a tarefa: ")
    else:
        task = " ".join(args)

    task_lower = task.lower()

    # Palavras-chave S1 (local grátis)
    s1_keywords = [
        "implementar", "codigo", "funcao", "metodo", "classe",
        "teste", "unit test", "pytest", "debug", "fix", "bug",
        "refatorar", "renomear", "extrair", "mover",
        "arquivo", "script", "batch", "shell", "python",
        "consertar", "corrigir", "ajustar", "criar arquivo",
        "escrever", "editar", "modificar", "atualizar",
        "executar comando", "rodar", "terminal", "comando",
        "git commit", "git add", "git push", "git pull",
        "ls", "cat", "grep", "find", "instalar",
        "config local", "ambiente", "venv", "pip",
        "docker", "dockerfile", "compose",
        "watchdog", "shellz", "vbs", "batch file",
    ]

    # Palavras-chave S2 (cloud leve)
    s2_keywords = [
        "arquitetura", "design", "planejar", "planejamento",
        "pesquisar", "pesquisa", "buscar", "google", "web search",
        "analisar", "analise de codigo", "code review",
        "explicar", "documentar", "docs", "readme",
        "comparar", "alternativas", "prós e contras",
        "roteiro", "roadmap", "estrategia",
    ]

    # Palavras-chave S3 (cloud pesado)
    s3_keywords = [
        "decisao", "decisão", "estrategico", "estrategia alta",
        "seguranca", "security", "cryptography",
        "legal", "contrato", "termos", "licenca",
        "negocio", "business", "investimento",
        "decidir", "decisao critica",
        "fallback", "emergencia", "critico",
    ]

    s1_score = sum(1 for kw in s1_keywords if kw in task_lower)
    s2_score = sum(1 for kw in s2_keywords if kw in task_lower)
    s3_score = sum(1 for kw in s3_keywords if kw in task_lower)

    if s3_score > s2_score and s3_score > s1_score and s3_score > 0:
        shell = "S3"
        model = "deepseek-pro"
        cost = "~$0.50/M 🧠"
        reason = f"Tarefa estratégica/crítica ({s3_score} matches)"
    elif s2_score >= s1_score and s2_score > 0:
        shell = "S2"
        model = "deepseek-v4-flash"
        cost = "~$0.15/M ☁️"
        reason = f"Tarefa de pesquisa/análise ({s2_score} matches)"
    else:
        shell = "S1"
        model = "qwen2.5-coder:7b (Ollama)"
        cost = "$0,00 🆓"
        reason = f"Tarefa de execução/código ({s1_score} matches)"

    print(json.dumps({
        "shell": shell,
        "model": model,
        "cost": cost,
        "reason": reason,
        "score": {"S1": s1_score, "S2": s2_score, "S3": s3_score},
    }, indent=2, ensure_ascii=False))

    print(f"\n➡️  Roteamento: {shell} ({model}) | {cost}")
    print(f"   > {reason}")
    return 0


def cmd_quota_check(args):
    """Verifica quota real via API ou simula."""
    # TODO: Implementar chamada real à API do provedor
    # Por enquanto simula baseado em arquivo de config
    config_path = "D:/projetos/hermes-watchdog/quota_config.json"
    
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        quota_remaining = config.get("quota_remaining", 50000)
        quota_total = config.get("quota_total", 500000)
    else:
        quota_remaining = 75000
        quota_total = 500000
        # Cria config padrão
        with open(config_path, 'w') as f:
            json.dump({"quota_remaining": quota_remaining, "quota_total": quota_total}, f)

    used = quota_total - quota_remaining
    pct_used = (used / quota_total) * 100
    pct_remaining = (quota_remaining / quota_total) * 100

    print(f"📊 QUOTA STATUS")
    print(f"   Total: {quota_total:,} tokens")
    print(f"   Usado: {used:,} ({pct_used:.1f}%)")
    print(f"   Restante: {quota_remaining:,} ({pct_remaining:.1f}%)")
    
    if pct_remaining < 20:
        print(f"   ⚠️  QUOTA BAIXA - Ativar modo economia (S1 prioritário)")
    elif pct_remaining < 50:
        print(f"   ⚠️  Quota moderada - Monitorar uso")
    else:
        print(f"   ✅ Quota saudável")

    return 0


import os


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help', 'help'):
        cmd_help(sys.argv[1:])
        return 0

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == 'intelligence-router':
        return cmd_intelligence_based_router(args)
    elif cmd == 'status':
        return cmd_status(args)
    elif cmd == 's1-router':
        return cmd_s1_router(args)
    elif cmd == 'quota-check':
        return cmd_quota_check(args)
    else:
        print(f"Comando desconhecido: {cmd}")
        print("Use 'hermes-workbench help' para ver os comandos disponíveis.")
        return 1


if __name__ == "__main__":
    sys.exit(main())