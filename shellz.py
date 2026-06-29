#!/usr/bin/env python3
"""
Shellz Router — Hermes S3/S1 Orchestrator
==========================================
Classifica tarefas e roteia para S1 (Ollama local, $0) ou S3 (DeepSeek cloud, $).

COMO O AGENTE HERMES USA ISSO:
  1. Chegou uma tarefa? Chame: python shellz.py classificar "descricao"
  2. Se retornar S1: execute via python s1_executor.py "tarefa" [--file path]
  3. Se retornar S3: processe voce mesmo (DeepSeek)
  4. SEMPRE reporte a economia ao final

Uso:
  python shellz.py classificar "descricao da tarefa"    → JSON com shell recomendado
  python shellz.py executar "descricao" [--file path]    → Executa no shell certo
  python shellz.py status                                → Status do sistema
  python shellz.py economia                              → Relatório da sessão
"""
import sys
import json
import os
import subprocess
import time
from datetime import datetime

# === CONFIG ===
S1_EXECUTOR = os.path.join(os.path.dirname(__file__), "s1_executor.py")
S1_MODEL = "qwen2.5-coder:7b"
S3_MODEL = "deepseek-v4-flash"
S3_RATE_PER_TOKEN = 0.15 / 1_000_000  # ~$0.15/M tokens

# === TASKS QUE S1 PODE FAZER ===
S1_TASKS = {
    # Shell puro (terminal, $0, zero LLM)
    "shell": [
        "ls", "grep", "find", "cat", "head", "tail", "wc", "du", "df",
        "pwd", "echo", "date", "whoami", "id", "uname",
        "cp", "mv", "rm", "mkdir", "touch", "chmod", "chown",
        "git status", "git diff", "git log", "git branch", "git stash",
        "git add", "git commit", "git push", "git pull", "git clone",
        "pip list", "pip freeze", "npm list",
        "sort", "uniq", "cut", "tr", "sed", "awk",
        "nslookup", "ping", "curl", "wget",
        "ps", "top", "htop", "kill", "systemctl",
        "docker ps", "docker images",
        "python --version", "node --version", "npm --version",
    ],
    # Precisa de LLM local (Ollama, $0)
    "ollama": [
        "balancear css", "verificar css", "check css",
        "consertar css", "corrigir css", "ajustar css",
        "analisar css", "css esta",
        "padding", "margem", "fonte", "font-size",
        "breakpoint", "responsivo", "viewport",
        "conferir", "verificar", "validar",
        "formatar", "indentar",
        "pequeno script", "script auxiliar",
        "contar linhas", "lines of code", "loc",
        "traduzir", "traducao",
    ],
}

# === TASKS QUE S3 DEVE FAZER (DeepSeek) ===
S3_TASKS = [
    "arquitetura", "design system", "arquitetar",
    "autenticacao", "auth", "login", "bcrypt", "senha",
    "criptografia", "AES", "hash",
    "planejar", "planejamento", "roadmap",
    "pesquisar", "pesquisa", "web search",
    "analise profunda", "analisar profundamente",
    "decisao", "decisão", "estrategico",
    "seguranca", "security", "vulnerabilidade",
    "logica nova", "logica complexa",
    "php", "banco de dados", "sql",
    "api externa", "integracao",
    "criar skill", "skill nova",
    "relatorio", "analise de dados",
]


def classify(task: str) -> dict:
    """Classify task into S1 or S3."""
    task_lower = task.lower()
    
    # Check S3 first (higher priority — security, auth, etc.)
    for kw in S3_TASKS:
        if kw in task_lower:
            return {
                "shell": "S3",
                "model": S3_MODEL,
                "reason": f"Palavra-chave S3: '{kw}'",
                "cost": "pago (~$0.15/M)",
                "action": "processar no DeepSeek",
            }
    
    # Check S1 shell tasks (puro, zero tokens)
    for kw in S1_TASKS["shell"]:
        if task_lower.startswith(kw) or task_lower.startswith(f"python {kw}"):
            return {
                "shell": "S1",
                "mode": "shell",
                "model": "shell (puro, $0)",
                "reason": f"Comando shell: '{kw}'",
                "cost": "$0,00",
                "action": f"executar via terminal diretamente",
            }
    
    # Check S1 Ollama tasks (precisa de LLM local)
    for kw in S1_TASKS["ollama"]:
        if kw in task_lower:
            return {
                "shell": "S1",
                "mode": "ollama",
                "model": S1_MODEL,
                "reason": f"Palavra-chave S1: '{kw}'",
                "cost": "$0,00 (local)",
                "action": f"executar via s1_executor.py no Ollama",
            }
    
    # Default: S3 (quando duvida, vai pro cloud)
    return {
        "shell": "S3",
        "model": S3_MODEL,
        "reason": "Sem keywords S1 ou S3 explicitas (default)",
        "cost": "pago (~$0.15/M)",
        "action": "processar no DeepSeek",
    }


def check_status() -> dict:
    """Check if Ollama is available for S1."""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {"ollama": True, "version": data.get("version", "?"), "s1": "disponivel"}
        return {"ollama": False, "error": "Ollama offline", "s1": "indisponivel"}
    except Exception as e:
        return {"ollama": False, "error": str(e), "s1": "indisponivel"}


def main():
    if len(sys.argv) < 2:
        print("Uso: python shellz.py classificar|executar|status|economia [...]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "classificar":
        task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not task:
            task = input("Descreva a tarefa: ")
        result = classify(task)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif action == "executar":
        task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not task:
            task = input("Descreva a tarefa: ")
        
        result = classify(task)
        
        if result["shell"] == "S1" and result.get("mode") == "shell":
            # Comando shell direto
            print(f"\n🐚 S1 (shell puro, $0)")
            print(f"{'='*40}")
            print(f"Comando: {task}")
            print()
            os.system(task)
            
        elif result["shell"] == "S1":
            # S1 via Ollama
            print(f"\n🐚 S1 ({S1_MODEL}, $0)")
            print(f"{'='*40}")
            r = subprocess.run(
                [sys.executable, S1_EXECUTOR, task],
                capture_output=True, text=True, timeout=120
            )
            print(r.stdout[-3000:] if r.stdout else "")
            if r.stderr:
                print(f"STDERR: {r.stderr[:1000]}")
                
        else:
            print(f"\n☁️  S3 ({S3_MODEL}, pago)")
            print(f"{'='*40}")
            print(f"Tarefa classificada como S3: {result['reason']}")
            print("Processe esta tarefa voce mesmo (no DeepSeek).")
        
    elif action == "status":
        status = check_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        
    elif action == "economia":
        print("Use `hermes insights --days 1` para telemetria real")
        
    else:
        print(f"Acao desconhecida: {action}")
        print("Uso: shellz.py classificar|executar|status|economia")


if __name__ == "__main__":
    main()
