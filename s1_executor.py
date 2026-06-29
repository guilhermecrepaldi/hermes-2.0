#!/usr/bin/env python3
"""
S1 Executor — Hermes Shell 1 (Ollama local, $0)
================================================
Executa tarefas no Ollama qwen2.5-coder:7b via API.
Usado pelo shellz.py e pelo agente Hermes para tarefas S1.

Uso:
  python s1_executor.py "sua tarefa ou pergunta"
  python s1_executor.py --file /caminho/arquivo.css "analise este CSS"
  python s1_executor.py --check-balance /caminho/arquivo.css

Retorna: JSON com {shell, model, output, tokens, cost_economy}
"""
import sys
import json
import subprocess
import os
import re
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
S1_MODEL = "qwen2.5-coder:7b"
S3_RATE_PER_TOKEN = 0.15 / 1_000_000  # DeepSeek v4 Flash: ~$0.15/M tokens


def call_ollama(prompt: str, model=S1_MODEL, max_tokens=2048) -> dict:
    """Call Ollama API and return full response."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.2,
        }
    })
    try:
        result = subprocess.run(
            ["curl", "-s", OLLAMA_URL, "-d", payload],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return {"error": f"curl failed: {result.stderr}"}
        data = json.loads(result.stdout)
        if "error" in data:
            return {"error": data["error"]}
        return data
    except subprocess.TimeoutExpired:
        return {"error": "Ollama timeout (60s)"}
    except Exception as e:
        return {"error": str(e)}


def check_css_balance(filepath: str) -> dict:
    """Check CSS file for unbalanced braces."""
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}
    
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    
    lines = content.split("\n")
    open_braces = 0
    close_braces = 0
    issues = []
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip comments
        if stripped.startswith("/*") or stripped.startswith("*"):
            continue
        
        open_braces += stripped.count("{")
        close_braces += stripped.count("}")
        
        # Check for likely issues
        if ":" in stripped and ";" not in stripped and not stripped.endswith("{") and not stripped.startswith("/*"):
            if i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("/*"):
                pass  # Could be multi-line value
        
        # Detect missing semicolons before closing brace
        if "}" in stripped and ";" not in lines[i-2] if i > 1 else True:
            prev = lines[i-2] if i > 1 else ""
            if prev.strip() and not prev.strip().endswith("{") and not prev.strip().startswith("/*") and ";" not in prev:
                issues.append(f"Linha {i-1}: possivel ';' faltando antes de '}}'")
    
    if open_braces != close_braces:
        return {
            "balanced": False,
            "opens": open_braces,
            "closes": close_braces,
            "diff": open_braces - close_braces,
            "issues": issues,
            "hint": "Faltam '}' no final" if close_braces < open_braces else "Sobram '}'",
        }
    
    return {
        "balanced": True,
        "opens": open_braces,
        "closes": close_braces,
        "diff": 0,
        "issues": issues[:5],
        "hint": "CSS balanceado OK" if not issues else f"{len(issues)} avisos de estilo",
    }


def execute_s1(task: str, filepath: str = None) -> dict:
    """Execute a task on S1 and return structured result."""
    
    # --- Tarefas shell puras (sem LLM) ---
    shell_only_patterns = [
        r"^(ls|grep|find|cat|head|tail|wc|du|df|pwd|echo|date|whoami|id)",
        r"^(git status|git diff|git log|git branch|git stash)",
        r"^(pip list|pip freeze|npm list)",
        r"^(cp|mv|rm|mkdir|touch|chmod|chown)",
    ]
    for pattern in shell_only_patterns:
        if re.match(pattern, task.strip(), re.IGNORECASE):
            try:
                result = subprocess.run(
                    task, shell=True, capture_output=True, text=True, timeout=30
                )
                return {
                    "shell": "S1",
                    "mode": "shell",
                    "model": "shell (puro, $0)",
                    "output": result.stdout[:5000] + (result.stderr[:1000] if result.stderr else ""),
                    "exit_code": result.returncode,
                    "tokens": 0,
                    "time_ms": 0,
                    "cost_economy": "$0,00 (shell puro)",
                }
            except subprocess.TimeoutExpired:
                return {"error": "Shell command timeout", "shell": "S1", "mode": "shell"}
            except Exception as e:
                return {"error": str(e), "shell": "S1", "mode": "shell"}
    
    # --- Check CSS balance ---
    if filepath and filepath.endswith(".css"):
        css_check = check_css_balance(filepath)
        if css_check["balanced"]:
            return {
                "shell": "S1",
                "mode": "css-check",
                "model": "local ($0)",
                "output": f"✅ CSS balanceado: {css_check['opens']} aberturas, {css_check['closes']} fechamentos",
                "tokens": 0,
                "time_ms": 0,
                "cost_economy": "$0,00",
            }
    
    # --- Tarefas que precisam de Ollama (LLM local) ---
    prompt = task
    if filepath and os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        # Truncate large files
        if len(content) > 8000:
            content = content[:8000] + "\n... [truncado]"
        prompt = f"Arquivo: {filepath}\n\n```\n{content}\n```\n\nTarefa: {task}"
    
    t0 = time.time()
    result = call_ollama(prompt)
    elapsed = time.time() - t0
    
    if "error" in result:
        return {"error": result["error"], "shell": "S1", "mode": "ollama"}
    
    tokens = result.get("eval_count", 0)
    economy = tokens * S3_RATE_PER_TOKEN
    
    return {
        "shell": "S1",
        "mode": "ollama",
        "model": S1_MODEL,
        "output": result.get("response", ""),
        "tokens": tokens,
        "time_ms": round(elapsed * 1000),
        "cost_economy": f"${economy:.4f} (economizados vs S3)",
        "s3_equivalent_cost": economy,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="S1 Executor — Ollama local tasks")
    parser.add_argument("task", nargs="*", help="Task description or command")
    parser.add_argument("--file", "-f", help="File path for context")
    parser.add_argument("--check-balance", help="CSS file to check balance")
    parser.add_argument("--json", action="store_true", help="Output as JSON only")
    args = parser.parse_args()
    
    if args.check_balance:
        result = check_css_balance(args.check_balance)
        result["shell"] = "S1"
        result["mode"] = "css-check"
        result["cost_economy"] = "$0,00"
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"🔍 CSS Check: {'✅ OK' if result.get('balanced') else '❌ DESBALANCEADO'}")
            print(f"   {{ {result.get('opens')} }} / }} {result.get('close_braces', result.get('closes'))}")
            if result.get("diff", 0) != 0:
                print(f"   Diferença: {result['diff']} (faltam {abs(result['diff'])} chaves)")
            if result.get("issues"):
                for issue in result["issues"][:3]:
                    print(f"   ⚠️  {issue}")
        return
    
    if not args.task:
        task = input("Task: ")
    else:
        task = " ".join(args.task)
    
    result = execute_s1(task, args.file)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"\n{'='*50}")
        print(f"🐚 S1 - {result.get('model', 'local')}")
        print(f"{'='*50}")
        print(f"💰 Custo: {result.get('cost_economy', '$0,00')}")
        if "tokens" in result and result["tokens"] > 0:
            print(f"📊 Tokens: {result['tokens']} ({result.get('time_ms', 0)}ms)")
        print()
        output = result.get("output", result.get("error", ""))
        if output:
            print(output[:3000])
        if len(output) > 3000:
            print(f"\n... [truncado, {len(output)} chars totais]")
        print()


if __name__ == "__main__":
    main()
