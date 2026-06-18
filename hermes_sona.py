#!/usr/bin/env python3
"""
HERMES SONA — Roteador Inteligente
Classifica tarefas em S1/S2/S3 usando Qwen3-VL local (Ollama)
Inspirado no Ruflo SONA (<0.05ms de decisão)

Uso:
  python hermes_sona.py "refatorar função de pagamento"
  python hermes_sona.py "arquitetar microsserviços" --verbose
  python hermes_sona.py "git status" --dry-run
"""

import sys
import json
import os
import urllib.request
import base64
import argparse

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
SONA_MODEL = "qwen3-vl:4b"

# Definição dos tiers (inspirado no Ruflo)
TIERS = {
    "S1": {
        "name": "Local (Ollama)",
        "model": "qwen2.5-coder:7b",
        "cost_per_m": 0.0,
        "description": "Tarefas simples: comandos shell, edição de arquivos, git básico",
        "max_tokens": 4096,
        "examples": ["git status", "ls -la", "editar README", "criar arquivo txt"],
    },
    "S2": {
        "name": "Cloud Médio (DeepSeek Flash)",
        "model": "deepseek-v4-flash",
        "cost_per_m": 0.15,
        "description": "Pesquisa, análise, debugging, revisão de código",
        "max_tokens": 8192,
        "examples": ["revisar PR", "debugar erro 500", "comparar frameworks"],
    },
    "S3": {
        "name": "Cloud Pesado (DeepSeek Pro)",
        "model": "deepseek-pro",
        "cost_per_m": 0.50,
        "description": "Arquitetura, decisões estratégicas, segurança, design de sistema",
        "max_tokens": 16384,
        "examples": ["arquitetar sistema", "analisar vulnerabilidade", "planejar roadmap"],
    },
}


def log(msg: str, level: str = "INFO"):
    print(f"[{level}] 🧠 {msg}")


def call_qwen(prompt: str, model: str = SONA_MODEL, max_tokens: int = 64) -> str:
    """Chama Qwen3-VL via Ollama API (sem imagem, só texto puro)."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": max_tokens},
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "").strip()
    except Exception as e:
        log(f"Erro Ollama: {e}", "WARN")
        return ""


def classify_task(task: str, verbose: bool = False) -> dict:
    """Classifica tarefa usando Qwen3-VL com prompting few-shot."""
    prompt = f"""Classifique a tarefa abaixo em UM dos três tiers:

S1 - Tarefa SIMPLES: comando shell, git, editar arquivo, criar script pequeno. Custo $0.
S2 - Tarefa MÉDIA: pesquisar, analisar, debug, revisar código. Custo ~$0.15/M.
S3 - Tarefa COMPLEXA: arquitetura, decisão estratégica, segurança, design de sistema. Custo ~$0.50/M.

Exemplos:
- "git status" → S1
- "revisar PR de autenticação" → S2
- "arquitetar microsserviço de pagamentos" → S3
- "criar arquivo de configuração" → S1
- "analisar vulnerabilidade no login" → S3
- "comparar React vs Vue" → S2

Tarefa: {task}

Responda APENAS com o tier: S1, S2 ou S3.
"""

    response = call_qwen(prompt)
    if not response:
        # Fallback: keyword matching simples
        return classify_task_keyword(task, verbose)

    # Extrair S1/S2/S3 da resposta
    response_upper = response.upper().strip()
    for tier in ["S3", "S2", "S1"]:
        if tier in response_upper:
            if verbose:
                log(f"Qwen3-VL classificou como {tier}: '{response[:100]}'")
            return {
                "tier": tier,
                "model": TIERS[tier]["model"],
                "cost": TIERS[tier]["cost_per_m"],
                "method": "qwen3-vl",
                "explanation": response[:200],
            }

    # Fallback extremo
    return classify_task_keyword(task, verbose)


def classify_task_keyword(task: str, verbose: bool = False) -> dict:
    """Classificador fallback por keywords."""
    task_lower = task.lower()

    # S3 — palavras de alta complexidade
    s3_keywords = [
        "arquitetura", "arquitetar", "decisão", "decisao", "estrategico",
        "estratégico", "seguranca", "segurança", "security", "cryptography",
        "legal", "contrato", "licenca", "licença", "business", "investimento",
        "roadmap", "planejamento", "design de sistema", "microservico",
        "microsserviço", "escalabilidade", "disponibilidade",
    ]

    # S2 — palavras de análise/pesquisa
    s2_keywords = [
        "pesquisar", "pesquisa", "analisar", "analise", "análise",
        "comparar", "alternativas", "review", "revisar", "debug",
        "depurar", "investigar", "documentar", "explicar",
        "benchmark", "performance", "otimizar", "otimização",
        "code review", "pull request", "pr",
    ]

    s3_score = sum(1 for kw in s3_keywords if kw in task_lower)
    s2_score = sum(1 for kw in s2_keywords if kw in task_lower)

    if s3_score > 0 and s3_score >= s2_score:
        tier = "S3"
    elif s2_score > 0:
        tier = "S2"
    else:
        tier = "S1"

    if verbose:
        log(f"Keyword match: S1={0}, S2={s2_score}, S3={s3_score} → {tier}")

    return {
        "tier": tier,
        "model": TIERS[tier]["model"],
        "cost": TIERS[tier]["cost_per_m"],
        "method": "keyword",
        "explanation": f"Classificado como {tier} por keyword matching",
    }


def main():
    parser = argparse.ArgumentParser(description="🧠 Hermes SONA Router")
    parser.add_argument("task", nargs="?", help="Tarefa a classificar")
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso")
    parser.add_argument("--dry-run", action="store_true", help="Não chamar Qwen3-VL")

    args = parser.parse_args()

    if not args.task:
        task = input("🧠 Descreva a tarefa para classificar: ")
    else:
        task = args.task

    if args.dry_run:
        result = classify_task_keyword(task, args.verbose)
    else:
        result = classify_task(task, args.verbose)

    tier = result["tier"]
    tier_info = TIERS[tier]

    print(f"\n{'=' * 60}")
    print(f"🧠 SONA — Relatório de Classificação")
    print(f"{'=' * 60}")
    print(f"📋 Tarefa: {task}")
    print(f"🎯 Tier:    {tier} — {tier_info['name']}")
    print(f"🤖 Modelo:  {tier_info['model']}")
    print(f"💰 Custo:   ${tier_info['cost_per_m']}/M tokens")
    print(f"🔍 Método:  {result['method']}")
    if args.verbose:
        print(f"📝 Detalhe: {result['explanation']}")
    print(f"{'=' * 60}")

    return 0


if __name__ == "__main__":
    main()
