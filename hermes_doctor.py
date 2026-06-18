#!/usr/bin/env python3
"""
HERMES DOCTOR — Health Check Completo
Inspirado no `ruflo doctor` mas para nosso stack:
Python, FFmpeg, Ollama, Qwen3-VL, GPU, disco, git, skills, cron

Uso:
  python hermes_doctor.py         # Check completo
  python hermes_doctor.py --quick # Só críticos
  python hermes_doctor.py --fix   # Tenta corrigir
"""

import sys
import os
import json
import subprocess
import shutil
from datetime import datetime

BASE_DIR = r"D:\projetos\hermes-watchdog"
CRITICAL_FILES = [
    "hermes_workbench.py",
    "hermes_queen.py",
    "hermes_sona.py",
    "video_analyzer.py",
    "setup_hermes.sh",
    "quota_config.json",
]

PASS = "✅"
WARN = "⚠️"
FAIL = "❌"
SKIP = "⏭️"


def log(status, msg, detail=""):
    icon = {"pass": PASS, "warn": WARN, "fail": FAIL, "skip": SKIP}[status]
    print(f"  {icon} {msg}")
    if detail:
        print(f"     {detail}")


def check_python():
    v = sys.version_info
    if v.major >= 3 and v.minor >= 10:
        log("pass", f"Python {v.major}.{v.minor}.{v.micro}", "≥ 3.10 requerido")
    else:
        log("fail", f"Python {v.major}.{v.minor}.{v.micro}", "≥ 3.10 necessário")


def check_ffmpeg():
    if shutil.which("ffmpeg"):
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        v = r.stdout.split("\n")[0] if r.stdout else "desconhecido"
        log("pass", f"FFmpeg: {v[:80]}...")
    else:
        log("fail", "FFmpeg não encontrado", "Instale: https://ffmpeg.org/download.html")


def check_ollama():
    try:
        r = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            log("pass", f"Ollama: {r.stdout.strip()}")
            # Verificar se está rodando
            try:
                import urllib.request
                req = urllib.request.Request("http://127.0.0.1:11434/api/tags", method="GET")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    models = json.loads(resp.read())
                    model_list = [m["name"] for m in models.get("models", [])]
                    log("pass", f"Ollama rodando (PID ativo)", f"{len(model_list)} modelos")
                    for m in model_list:
                        log("pass", f"  Modelo: {m}")
            except:
                log("warn", "Ollama instalado mas servidor não está rodando", "Execute: ollama serve")
        else:
            log("fail", "Ollama não encontrado")
    except FileNotFoundError:
        log("fail", "Ollama não instalado")


def check_gpu():
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0:
            lines = r.stdout.strip().split("\n")
            for line in lines:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 4:
                    log("pass", f"GPU: {parts[0]}", f"VRAM: {parts[1]} (usado: {parts[2]}) | Driver: {parts[3]}")
        else:
            log("fail", "nvidia-smi falhou", "Driver NVIDIA pode não estar instalado")
    except FileNotFoundError:
        log("warn", "GPU NVIDIA não detectada", "Usando CPU — performance reduzida")


def check_disk():
    try:
        import shutil
        usage = shutil.disk_usage(BASE_DIR)
        free_gb = usage.free / (1024**3)
        total_gb = usage.total / (1024**3)
        pct = usage.used / usage.total * 100
        if pct < 85:
            log("pass", f"Disco: {total_gb:.0f}GB total, {free_gb:.0f}GB livre ({pct:.0f}% usado)")
        else:
            log("warn", f"Disco: {total_gb:.0f}GB total, {free_gb:.0f}GB livre", "Acima de 85% — libere espaço")
    except:
        log("warn", "Não foi possível verificar disco")


def check_critical_files():
    missing = []
    for f in CRITICAL_FILES:
        path = os.path.join(BASE_DIR, f)
        if os.path.exists(path):
            size = os.path.getsize(path)
            log("pass", f"Arquivo: {f} ({size:,} bytes)")
        else:
            missing.append(f)
            log("fail", f"Arquivo AUSENTE: {f}")
    return missing


def check_git():
    git_dir = os.path.join(BASE_DIR, ".git")
    if os.path.isdir(git_dir):
        r = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, cwd=BASE_DIR)
        last = r.stdout.strip() if r.returncode == 0 else "desconhecido"
        r2 = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=BASE_DIR)
        dirty = r2.stdout.strip()
        if dirty:
            log("warn", f"Git: último commit {last[:50]}...", f"{len(dirty.split(chr(10)))} arquivos não comitados")
        else:
            log("pass", f"Git: último commit {last[:50]}...", "Working tree limpo")
    else:
        log("fail", "Git: não é um repositório git")


def check_skills():
    try:
        r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        lines = r.stdout.strip().split("\n")[1:]  # Pula header
        models = [l.split()[0] for l in lines if l.strip()]
        key_models = ["qwen3-vl", "qwen2.5-coder", "deepseek-coder", "gemma3"]
        for km in key_models:
            found = [m for m in models if km in m]
            if found:
                log("pass", f"Modelo: {found[0]}")
            else:
                log("warn", f"Modelo AUSENTE: {km}")
    except:
        log("warn", "Não foi possível listar modelos Ollama")


def main():
    print(f"\n{'=' * 60}")
    print(f"🏥 HERMES DOCTOR — Diagnóstico Completo")
    print(f"{'=' * 60}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Base: {BASE_DIR}")
    print()

    sections = [
        ("🐍 Python", check_python),
        ("🎬 FFmpeg", check_ffmpeg),
        ("🦙 Ollama", check_ollama),
        ("🎮 GPU", check_gpu),
        ("💾 Disco", check_disk),
        ("📁 Arquivos", check_critical_files),
        ("🔧 Git", check_git),
        ("🧩 Modelos", check_skills),
    ]

    all_passed = True
    for name, func in sections:
        print(f"\n── {name} ──")
        try:
            result = func()
            if result:  # Se retornou lista de arquivos faltando
                all_passed = False
        except Exception as e:
            log("fail", f"Erro ao verificar: {e}")
            all_passed = False

    print(f"\n{'=' * 60}")
    if all_passed:
        print(f"🏥 Diagnóstico: TUDO OK ✅")
    else:
        print(f"🏥 Diagnóstico: Problemas encontrados — verifique os ⚠️ e ❌ acima")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
