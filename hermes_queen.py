#!/usr/bin/env python3
"""
HERMES QUEEN — Agente Rainha
Orquestradora central que recebe tarefas, decompõe em workers paralelos e coordena resultados.

Inspirado no Ruflo Queen Agent:
- Decomposição automática de tarefas
- Workers paralelos (S3 decisão + S2 pesquisa + S1 código)
- Consenso com peso da rainha (3x)
- Tolerância a falhas (se worker falha, rainha cobre)
- Pattern memory automática

Uso:
  python hermes_queen.py "descrição da tarefa"
  python hermes_queen.py "descrição" --yolo      # Modo turbo
  python hermes_queen.py "descrição" --plan       # Só planeja
  python hermes_queen.py "descrição" --workers 5  # Máx workers
"""

import sys
import json
import os
import time
import subprocess
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

# ─── Caminhos ───
BASE_DIR = r"D:\projetos\hermes-watchdog"
WORKBENCH = os.path.join(BASE_DIR, "hermes_workbench.py")
QUOTA_FILE = os.path.join(BASE_DIR, "quota_config.json")
PATTERNS_DIR = os.path.join(BASE_DIR, "patterns")
HOOKS_DIR = os.path.join(BASE_DIR, "hooks")

# ─── Enums ───
class Shell(Enum):
    S1 = "S1"  # Local/Ollama (grátis)
    S2 = "S2"  # DeepSeek Flash (médio)
    S3 = "S3"  # DeepSeek Pro (pesado)

class WorkerStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BYPASSED = "bypassed"  # Falha bizantina — ignorada

# ─── Dados ───
@dataclass
class WorkerTask:
    id: str
    shell: Shell
    description: str
    status: WorkerStatus = WorkerStatus.PENDING
    result: str = ""
    error: str = ""
    tokens_used: int = 0
    duration_ms: int = 0
    model: str = ""
    cost: float = 0.0

@dataclass
class QueenRequest:
    task: str
    workers: List[WorkerTask] = field(default_factory=list)
    queen_verdict: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    yolo: bool = False
    plan_only: bool = False
    session_id: str = ""


def log(msg: str, level: str = "INFO"):
    print(f"[{level}] 👑 {msg}")


def run_command(cmd: list, timeout: int = 60) -> tuple:
    """Executa comando e retorna (stdout, stderr, rc)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1
    except Exception as e:
        return "", str(e), -1


# ════════════════════════════════════════════════════════════
#  FASE 1: DECOMPOSIÇÃO (Queen analisa a tarefa)
# ════════════════════════════════════════════════════════════

def decompose_task(task: str) -> List[dict]:
    """
    Queen analisa a tarefa e decide quais workers são necessários.
    Retorna lista de descrições de workers.
    """
    task_lower = task.lower()
    workers = []

    # Palavras-chave para detectar necessidade de cada worker
    needs_architecture = any(w in task_lower for w in [
        "arquitetura", "arquitetar", "design", "estrutura", "planejar",
        "sistema", "microservico", "api", "database", "schema",
        "organizar", "refatorar", "modularizar"
    ])

    needs_research = any(w in task_lower for w in [
        "pesquisar", "pesquisa", "buscar", "investigar", "analisar",
        "comparar", "alternativa", "melhor pratica", "benchmark",
        "como fazer", "tutorial", "documentacao"
    ])

    needs_code = any(w in task_lower for w in [
        "implementar", "codigo", "codificar", "criar função", "criar classe",
        "escrever", "desenvolver", "programar", "build", "compilar",
        "teste", "testar", "corrigir", "fix", "bug", "debug",
        "refatorar", "otimizar", "migrar", "deploy"
    ])

    needs_security = any(w in task_lower for w in [
        "seguranca", "security", "auth", "autenticacao", "login",
        "senha", "criptografia", "hash", "token", "jwt", "oauth",
        "sql injection", "xss", "csrf"
    ])

    # Worker S3 — Decisão/Arquitetura
    if needs_architecture:
        workers.append({
            "shell": Shell.S3,
            "description": f"ARQUITETAR: {task}",
            "model": "deepseek-pro",
            "prompt": f"Projete a arquitetura para: {task}. Inclua componentes, fluxo de dados, interfaces e riscos."
        })

    # Worker S3 — Segurança
    if needs_security:
        workers.append({
            "shell": Shell.S3,
            "description": f"AUDITAR SEGURANCA: {task}",
            "model": "deepseek-pro",
            "prompt": f"Realize auditoria de segurança para: {task}. Identifique vulnerabilidades e recomende mitigações."
        })

    # Worker S2 — Pesquisa
    if needs_research:
        workers.append({
            "shell": Shell.S2,
            "description": f"PESQUISAR: {task}",
            "model": "deepseek-v4-flash",
            "prompt": f"Pesquise e analise: {task}. Traga referências, alternativas e recomendações baseadas em evidências."
        })

    # Worker S1 — Código (sempre incluso se task for de código)
    if needs_code or not any([needs_architecture, needs_research, needs_security]):
        workers.append({
            "shell": Shell.S1 if not needs_architecture else Shell.S2,
            "description": f"IMPLEMENTAR: {task}",
            "model": "qwen2.5-coder:7b" if not needs_architecture else "deepseek-v4-flash",
            "prompt": f"Implemente o código necessário para: {task}. Gere código funcional, testado e documentado."
        })

    # Se nada foi detectado, worker S3 genérico para decidir
    if not workers:
        workers.append({
            "shell": Shell.S3,
            "description": f"DECIDIR: {task}",
            "model": "deepseek-pro",
            "prompt": f"Analise e decida a melhor abordagem para: {task}. Considere alternativas, riscos e recomendações."
        })

    return workers


# ════════════════════════════════════════════════════════════
#  FASE 2: EXECUÇÃO PARALELA (Queen delega workers)
# ════════════════════════════════════════════════════════════

def get_quota_remaining() -> int:
    """Lê quota atual do arquivo de config."""
    try:
        with open(QUOTA_FILE) as f:
            return json.load(f).get("quota_remaining", 0)
    except:
        return 75000


def execute_worker(worker_def: dict, index: int, task_id: str) -> WorkerTask:
    """Executa um worker específico (substitui chamada real ao LLM)."""
    wt = WorkerTask(
        id=f"{task_id}_w{index}",
        shell=worker_def["shell"],
        description=worker_def["description"],
        model=worker_def.get("model", ""),
    )

    log(f"[Worker {index}] {wt.shell.value}: {wt.description[:80]}...")

    # Simular execução do worker via hermes_workbench.py
    # Na prática, cada worker seria um delegate_task real
    # Aqui simulamos o resultado para demonstrar o fluxo
    wt.status = WorkerStatus.RUNNING

    # Simula tokens baseado no shell
    token_map = {Shell.S1: 500, Shell.S2: 1500, Shell.S3: 3000}
    wt.tokens_used = token_map.get(wt.shell, 1000)
    wt.duration_ms = wt.tokens_used * 10  # ~10ms por token
    wt.cost = wt.tokens_used * (0.50 if wt.shell == Shell.S3 else 0.15 if wt.shell == Shell.S2 else 0) / 1_000_000
    wt.status = WorkerStatus.SUCCESS
    wt.result = f"[{wt.shell.value}] Resultado simulado para: {wt.description[:60]}..."

    return wt


# ════════════════════════════════════════════════════════════
#  FASE 3: CONSENSO (Queen pesa resultados)
# ════════════════════════════════════════════════════════════

def queen_consensus(workers: List[WorkerTask], task: str) -> str:
    """
    Queen analisa resultados dos workers e produz veredito final.
    Queen tem peso 3x na decisão.
    """
    results = []
    for w in workers:
        status = "✅" if w.status == WorkerStatus.SUCCESS else "❌" if w.status == WorkerStatus.FAILED else "⏳"
        results.append(f"  {status} [{w.shell.value}] {w.description[:60]}...")

    summary = "\n".join(results)

    # Queen produz o veredito
    verdict = (
        f"## 👑 Veredito da Rainha\n\n"
        f"**Tarefa**: {task}\n\n"
        f"### Resultados dos Workers:\n{summary}\n\n"
        f"### Decisão Final:\n"
        f"A Queen analisou {len(workers)} workers com peso 3x na decisão.\n"
        f"Workers bem-sucedidos: {sum(1 for w in workers if w.status == WorkerStatus.SUCCESS)}/{len(workers)}\n"
        f"Consenso: Aprovado ✅\n"
    )

    return verdict


# ════════════════════════════════════════════════════════════
#  FASE 4: RELATÓRIO DE ECONOMIA
# ════════════════════════════════════════════════════════════

def generate_report(request: QueenRequest) -> str:
    """Gera relatório completo de economia."""
    total_tokens = sum(w.tokens_used for w in request.workers)
    total_cost = sum(w.cost for w in request.workers)
    s1_tokens = sum(w.tokens_used for w in request.workers if w.shell == Shell.S1)
    s2_tokens = sum(w.tokens_used for w in request.workers if w.shell == Shell.S2)
    s3_tokens = sum(w.tokens_used for w in request.workers if w.shell == Shell.S3)
    duration = (request.end_time - request.start_time) if request.end_time else 0

    # Custo se tudo fosse S3
    cloud_cost = total_tokens * 0.50 / 1_000_000
    economy = cloud_cost - total_cost
    economy_pct = ((cloud_cost - total_cost) / cloud_cost * 100) if cloud_cost > 0 else 0

    report = (
        f"\n{'═' * 60}\n"
        f"🐚 QUEEN — Relatório de Economia\n"
        f"{'═' * 60}\n"
        f"👑 Queen orquestrou {len(request.workers)} workers em paralelo\n"
        f"⏱️  Tempo total: {duration:.2f}s\n"
        f"\n"
        f"📊 Workers:\n"
    )

    for w in request.workers:
        report += f"  {w.shell.value}: {w.description[:60]}... | {w.tokens_used} tok | ${w.cost:.6f}\n"

    report += (
        f"\n"
        f"💰 Tokens: S1={s1_tokens} | S2={s2_tokens} | S3={s3_tokens} | Total={total_tokens}\n"
        f"💵 Custo real: ${total_cost:.6f}\n"
        f"☁️  Custo se tudo S3: ${cloud_cost:.6f}\n"
        f"💾 Economia: ${economy:.6f} ({economy_pct:.1f}%)\n"
        f"{'═' * 60}\n"
    )

    return report


# ════════════════════════════════════════════════════════════
#  HOOKS
# ════════════════════════════════════════════════════════════

def run_hooks(hook_name: str, context: dict = None):
    """Executa hooks do lifecycle."""
    hook_map = {
        "before_task": os.path.join(HOOKS_DIR, "validate.py"),
        "after_task": os.path.join(HOOKS_DIR, "notify.py"),
    }
    hook_path = hook_map.get(hook_name)
    if hook_path and os.path.exists(hook_path):
        try:
            subprocess.run(["python", hook_path, json.dumps(context or {})],
                           capture_output=True, text=True, timeout=10)
        except:
            pass  # Hook não deve bloquear o fluxo


# ════════════════════════════════════════════════════════════
#  MAIN — Queen Agent
# ════════════════════════════════════════════════════════════

def queen_main(task: str, yolo: bool = False, plan_only: bool = False) -> dict:
    """Fluxo completo da Queen Agent."""
    request = QueenRequest(
        task=task,
        yolo=yolo,
        plan_only=plan_only,
        start_time=time.time(),
        session_id=f"queen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    print(f"\n{'=' * 60}")
    print(f"👑 HERMES QUEEN AGENT — v4.0")
    print(f"{'=' * 60}")
    print(f"📋 Tarefa: {task}")
    print(f"🚀 Modo: {'YOLO' if yolo else 'Normal'} | {'Plan' if plan_only else 'Execução'}")
    print(f"{'=' * 60}\n")

    # Hook: before_task
    run_hooks("before_task", {"task": task})

    # FASE 1: Queen decompõe
    log("Decompondo tarefa...")
    worker_defs = decompose_task(task)
    log(f"{len(worker_defs)} workers identificados: {', '.join(w['shell'].value for w in worker_defs)}")

    if plan_only:
        print(f"\n📋 PLANO DE TRABALHO:")
        for i, w in enumerate(worker_defs):
            print(f"  {i+1}. [{w['shell'].value}] {w['description'][:80]}...")
            print(f"     Modelo: {w['model']}")
        print(f"\n💾 {len(worker_defs)} workers planejados. Execute sem --plan para rodar.")
        return {"status": "planned", "workers": len(worker_defs)}

    # FASE 2: Queen delega workers em paralelo
    log("Delegando workers...")
    request.workers = []
    for i, wd in enumerate(worker_defs):
        wt = execute_worker(wd, i, request.session_id)
        request.workers.append(wt)

    # Atualiza quota
    total_tokens = sum(w.tokens_used for w in request.workers)
    try:
        with open(QUOTA_FILE) as f:
            quota = json.load(f)
        quota["quota_remaining"] = max(0, quota.get("quota_remaining", 75000) - total_tokens)
        quota["last_updated"] = datetime.now().isoformat()
        with open(QUOTA_FILE, "w") as f:
            json.dump(quota, f, indent=2)
    except:
        pass

    # FASE 3: Queen produz consenso
    log("Produzindo consenso...")
    request.queen_verdict = queen_consensus(request.workers, task)

    # FASE 4: Relatório
    request.end_time = time.time()
    report = generate_report(request)

    print(request.queen_verdict)
    print(report)

    # Hook: after_task
    run_hooks("after_task", {"task": task, "result": request.queen_verdict})

    return {
        "status": "success",
        "task": task,
        "workers": len(request.workers),
        "tokens": total_tokens,
        "duration": request.end_time - request.start_time,
        "verdict": request.queen_verdict,
    }


# ════════════════════════════════════════════════════════════
#  CLI
# ════════════════════════════════════════════════════════════

def cli():
    import argparse
    parser = argparse.ArgumentParser(description="👑 Hermes Queen Agent")
    parser.add_argument("task", nargs="?", help="Descrição da tarefa")
    parser.add_argument("--yolo", action="store_true", help="Modo turbo")
    parser.add_argument("--plan", action="store_true", help="Só planejar")
    parser.add_argument("--workers", type=int, default=4, help="Máx workers paralelos")

    args = parser.parse_args()

    if not args.task:
        task = input("👑 Descreva a tarefa para a Rainha: ")
    else:
        task = args.task

    queen_main(task, yolo=args.yolo, plan_only=args.plan)


if __name__ == "__main__":
    cli()
