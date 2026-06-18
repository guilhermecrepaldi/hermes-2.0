#!/usr/bin/env python3
"""
Hermes Workbench - S1 Router
Decide se uma tarefa pode ser executada no S1 (Ollama local = gratis)
ou precisa de S2/S3 (DeepSeek cloud = pago).

Uso: python s1_router.py "descricao da tarefa"
Retorno: "S1" | "S2" | "S3" + justificativa
"""
import sys
import json

# Tarefas que S1 (Ollama/qwen2.5-coder:7b) pode fazer bem
S1_CAPABILITIES = {
    "keywords": [
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
    "max_tokens": 4096,
    "model": "qwen2.5-coder:7b",
    "cost": "$0,00 🆓",
}

# Tarefas que precisam de S2 (DeepSeek V4 Flash - cloud leve)
S2_CAPABILITIES = {
    "keywords": [
        "arquitetura", "design", "planejar", "planejamento",
        "pesquisar", "pesquisa", "buscar", "google", "web search",
        "analisar", "analise de codigo", "code review",
        "explicar", "documentar", "docs", "readme",
        "comparar", "alternativas", "prós e contras",
        "roteiro", "roadmap", "estrategia",
    ],
    "model": "deepseek-v4-flash",
    "cost": "~$0.15/M ☁️",
}

# Tarefas que exigem S3 (deepseek-pro - cloud pesado)
S3_CAPABILITIES = {
    "keywords": [
        "decisao", "decisão", "estrategico", "estrategia alta",
        "seguranca", "security", "cryptography",
        "legal", "contrato", "termos", "licenca",
        "negocio", "business", "investimento",
        "decidir", "decisao critica",
        "fallback", "emergencia", "critico",
    ],
    "model": "deepseek-pro",
    "cost": "~$0.50/M 🧠",
}


def classify_task(task: str) -> dict:
    task_lower = task.lower()
    
    # Count keyword matches for each shell
    s1_score = sum(1 for kw in S1_CAPABILITIES["keywords"] if kw in task_lower)
    s2_score = sum(1 for kw in S2_CAPABILITIES["keywords"] if kw in task_lower)
    s3_score = sum(1 for kw in S3_CAPABILITIES["keywords"] if kw in task_lower)
    
    # Decision logic
    if s3_score > s2_score and s3_score > s1_score and s3_score > 0:
        return {
            "shell": "S3",
            "model": S3_CAPABILITIES["model"],
            "cost": S3_CAPABILITIES["cost"],
            "reason": f"Tarefa estrategica/critica ({s3_score} matches)",
            "score": {"S1": s1_score, "S2": s2_score, "S3": s3_score},
        }
    elif s2_score >= s1_score and s2_score > 0:
        return {
            "shell": "S2",
            "model": S2_CAPABILITIES["model"],
            "cost": S2_CAPABILITIES["cost"],
            "reason": f"Tarefa de pesquisa/analise ({s2_score} matches)",
            "score": {"S1": s1_score, "S2": s2_score, "S3": s3_score},
        }
    else:
        return {
            "shell": "S1",
            "model": S1_CAPABILITIES["model"],
            "cost": S1_CAPABILITIES["cost"],
            "reason": f"Tarefa de execucao/codigo ({s1_score} matches)",
            "score": {"S1": s1_score, "S2": s2_score, "S3": s3_score},
        }


def main():
    if len(sys.argv) < 2:
        task = input("Descreva a tarefa: ")
    else:
        task = " ".join(sys.argv[1:])
    
    result = classify_task(task)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Summary line
    print(f"\n➡️  Roteamento: {result['shell']} ({result['model']}) | {result['cost']}")
    print(f"   > {result['reason']}")


if __name__ == "__main__":
    main()
