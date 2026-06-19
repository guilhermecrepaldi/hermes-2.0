#!/usr/bin/env python3
"""Hermes Workbench - S1 Router
Decide se uma tarefa pode ser executada no S1 (Ollama local = gratis)
ou precisa de S2/S3 (DeepSeek cloud = pago).

Uso: python s1_router.py "descricao da tarefa"
Retorno: RouterDecision com shell, modelo, custo e justificativa.
"""
from __future__ import annotations
import sys, re, json
from core import RouterDecision, ShellCapability


# --- Capacidades das shells ---

S1: ShellCapability = ShellCapability(
    name="S1 - Executor (local/Ollama)",
    keywords=[
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
    ],
    max_tokens=4096,
    model="qwen2.5-coder:7b",
    cost="$0,00 🆓",
    priority=3,
)

S2: ShellCapability = ShellCapability(
    name="S2 - Arquiteto (DeepSeek Flash - cloud leve)",
    keywords=[
        "arquitetura", "design", "planejar", "planejamento",
        "pesquisar", "pesquisa", "buscar", "google", "web search",
        "analisar", "analise de codigo", "code review",
        "explicar", "documentar", "docs", "readme",
        "comparar", "alternativas", "prós e contras",
        "roteiro", "roadmap", "estrategia",
    ],
    max_tokens=8192,
    model="deepseek-v4-flash",
    cost="~$0.15/M ☁️",
    priority=2,
)

S3: ShellCapability = ShellCapability(
    name="S3 - Gestor (deepseek-pro - cloud pesado)",
    keywords=[
        "decisao", "decisão", "estrategico", "estrategia alta",
        "seguranca", "security", "cryptography",
        "legal", "contrato", "termos", "licenca",
        "negocio", "business", "investimento",
        "decidir", "decisao critica",
        "fallback", "emergencia", "critico",
    ],
    max_tokens=16384,
    model="deepseek-pro",
    cost="~$0.50/M 🧠",
    priority=1,
)

SHELLS: list[ShellCapability] = [S1, S2, S3]


def _kw_match(keyword: str, text: str) -> bool:
    """Match de keyword com word boundary. Evita falsos positivos."""
    return bool(re.search(rf"\b{re.escape(keyword)}\b", text.lower()))


def classify_task(task: str) -> RouterDecision:
    """Classifica uma tarefa em S1, S2 ou S3 baseado em keywords."""
    scores = [
        sum(1 for kw in shell.keywords if _kw_match(kw, task))
        for shell in SHELLS
    ]
    s1_score, s2_score, s3_score = scores

    # Decisao: maior score vence, com fallback S1
    if s3_score > s2_score and s3_score > s1_score and s3_score > 0:
        return RouterDecision(
            shell="S3", model=S3.model, cost=S3.cost,
            reason=f"Tarefa estrategica/critica ({s3_score} matches)",
            score_s1=s1_score, score_s2=s2_score, score_s3=s3_score,
        )
    elif s2_score >= s1_score and s2_score > 0:
        return RouterDecision(
            shell="S2", model=S2.model, cost=S2.cost,
            reason=f"Tarefa de pesquisa/analise ({s2_score} matches)",
            score_s1=s1_score, score_s2=s2_score, score_s3=s3_score,
        )
    else:
        return RouterDecision(
            shell="S1", model=S1.model, cost=S1.cost,
            reason=f"Tarefa de execucao/codigo ({s1_score} matches)",
            score_s1=s1_score, score_s2=s2_score, score_s3=s3_score,
        )


def main() -> int:
    """Entry point da CLI."""
    if len(sys.argv) < 2:
        task = input("Descreva a tarefa: ")
    else:
        task = " ".join(sys.argv[1:])

    result = classify_task(task)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    print(f"\n➡️  Roteamento: {result.shell} ({result.model}) | {result.cost}")
    print(f"   > {result.reason}")
    return 0


if __name__ == "__main__":
    main()
