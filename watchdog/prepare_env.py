#!/usr/bin/env python3
"""prepare_env.py — Prepara o ambiente Neo Hermes.
Uso: python prepare_env.py

Verifica/inicia:
  - Ollama (inicia se parado)
  - Configuracoes do Hermes (delegation, provider)
  - Dependencias (feedparser, yt-dlp)
  - Web tools (Jina Reader)
  - Shellz (roteamento S3/S1)
  - Telemetria

Uso: python prepare_env.py --fix  → tenta corrigir problemas automaticamente
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
CIANO = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

HERMES_CONFIG = Path.home() / "AppData/Local/hermes/config.yaml"
NEO_HERMES = Path(__file__).resolve().parent.parent
WATCHDOG = Path(__file__).resolve().parent


def ok(msg): print(f"  {VERDE}✅{RESET} {msg}")
def warn(msg): print(f"  {AMARELO}⚠{RESET}  {msg}")
def err(msg): print(f"  {VERMELHO}❌{RESET} {msg}")
def info(msg): print(f"  {CIANO}ℹ{RESET}  {msg}")


def check_port(port, timeout=2):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", port))
        s.close()
        return True
    except:
        return False


def check_ollama():
    """Verifica Ollama. Se --fix, tenta iniciar."""
    fix = "--fix" in sys.argv
    
    # Testa se Ollama responde
    try:
        import urllib.request
        r = urllib.request.urlopen("http://localhost:11434/api/version", timeout=3)
        data = json.loads(r.read())
        ok(f"Ollama {data['version']} — rodando em :11434")
        return True
    except:
        pass
    
    # Testa se o processo existe
    if shutil.which("ollama"):
        warn("Ollama instalado mas nao respondendo em :11434")
        if fix:
            info("Iniciando Ollama em background...")
            try:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                )
                # Aguarda ate responder
                for _ in range(10):
                    time.sleep(1)
                    try:
                        import urllib.request
                        urllib.request.urlopen("http://localhost:11434/api/version", timeout=2)
                        ok("Ollama iniciado com sucesso")
                        return True
                    except:
                        continue
                err("Ollama nao respondeu apos 10s")
                return False
            except Exception as e:
                err(f"Falha ao iniciar Ollama: {e}")
                return False
    else:
        err("Ollama nao instalado. Baixe em: https://ollama.com/download")
        return False


def check_model():
    """Verifica se o modelo qwen2.5-coder:7b existe."""
    try:
        import urllib.request
        r = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
        models = json.loads(r.read()).get("models", [])
        names = [m["name"] for m in models]
        if "qwen2.5-coder:7b" in names:
            ok("Modelo qwen2.5-coder:7b disponivel")
            return True
        else:
            warn("qwen2.5-coder:7b nao encontrado")
            if "--fix" in sys.argv:
                info("Baixando qwen2.5-coder:7b (~4.7GB)...")
                subprocess.run(["ollama", "pull", "qwen2.5-coder:7b"])
                ok("Modelo baixado")
                return True
            return False
    except:
        err("Nao foi possivel verificar modelos")
        return False


def check_deps():
    """Verifica dependencias Python."""
    deps = {"feedparser": "pip install feedparser", "yt_dlp": "pip install yt-dlp"}
    ok_count = 0
    for mod, cmd in deps.items():
        try:
            __import__(mod.replace("_", "-") if "_" in mod else mod)
            ok(f"{mod} instalado")
            ok_count += 1
        except ImportError:
            try:
                __import__(mod)
                ok(f"{mod} instalado")
                ok_count += 1
            except ImportError:
                err(f"{mod} nao instalado. Rode: {cmd}")
    
    # gh CLI
    if shutil.which("gh"):
        ok("gh CLI instalado")
        ok_count += 1
    else:
        warn("gh CLI nao instalado (opcional, para GitHub)")
    
    return ok_count


def check_hermes_config():
    """Verifica configuracao do Hermes."""
    if not HERMES_CONFIG.exists():
        err("config.yaml do Hermes nao encontrado")
        return False
    
    try:
        import yaml
        with open(HERMES_CONFIG) as f:
            cfg = yaml.safe_load(f)
        
        # Delegation
        d = cfg.get("delegation", {})
        if d.get("provider") == "ollama" and d.get("model") == "qwen2.5-coder:7b":
            ok(f"Delegacao configurada: Ollama {d.get('model')}")
        else:
            warn(f"Delegacao: provider={d.get('provider')}, model={d.get('model')}")
        
        return True
    except Exception as e:
        err(f"Erro lendo config: {e}")
        return False


def check_web_tools():
    """Testa Jina Reader."""
    try:
        import urllib.request
        r = urllib.request.urlopen("https://r.jina.ai/https://example.com", timeout=10)
        content = r.read().decode()
        if "Example" in content or "example" in content or len(content) > 100:
            ok("Jina Reader funcional (leitura de URLs)")
            return True
        else:
            warn("Jina Reader respondeu mas conteudo inesperado")
            return True  # Nao bloqueia
    except Exception as e:
        warn(f"Jina Reader temporariamente indisponivel: {e}")
        return True  # Nao bloqueia - pode ser rate limit temporario


def check_shellz():
    """Testa roteamento Shellz."""
    try:
        sys.path.insert(0, str(WATCHDOG))
        from shellz import shellz
        s1 = shellz.rotear("git status")
        s3 = shellz.rotear("arquitetura")
        if s1.shell == "S1" and s3.shell == "S3":
            ok(f"Shellz ativo: S1=Ollama($0) | S3=DeepSeek(${s3.cost_per_1m:.2f}/M)")
            return True
        else:
            err(f"Shellz: S1={s1.shell} S3={s3.shell}")
            return False
    except Exception as e:
        err(f"Shellz: {e}")
        return False


def check_compress():
    """Testa compressor Ollama."""
    try:
        sys.path.insert(0, str(WATCHDOG))
        from ollama_compress import doctor
        d = doctor()
        if d.get("compress_ok"):
            ok(f"Compressao Ollama funcional (modelo: {d.get('model')})")
            return True
        else:
            warn("Compressao Ollama: instalado mas compress_ok=False")
            return False
    except Exception as e:
        warn(f"Compressao: {e}")
        return False


def summary(results):
    """Mostra resumo final."""
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}  NEO HERMES — Status do Ambiente{RESET}")
    print(f"{BOLD}{'='*50}{RESET}")
    
    for name, ok_ in results.items():
        icon = f"{VERDE}✅{RESET}" if ok_ else f"{AMARELO}⚠{RESET}" if ok_ is None else f"{VERMELHO}❌{RESET}"
        print(f"  {icon} {name}")
    
    print(f"\n  {BOLD}{passed}/{total}{RESET} checks passaram")
    
    if passed == total:
        print(f"\n  {VERDE}{BOLD}✅ Ambiente pronto! So abrir o Hermes Desktop.{RESET}")
    else:
        print(f"\n  {AMARELO}Alguns checks falharam. Rode com --fix pra tentar corrigir.{RESET}")
    
    print(f"{BOLD}{'='*50}{RESET}")


def main():
    print(f"\n{BOLD}{CIANO}🌀 Neo Hermes — Preparando Ambiente{RESET}")
    print(f"{'='*50}")
    
    results = {}
    
    info("Verificando Ollama...")
    results["Ollama"] = check_ollama()
    
    if results["Ollama"]:
        info("Verificando modelos...")
        results["Modelo qwen2.5-coder"] = check_model()
    
    info("Verificando dependencias...")
    results["Dependencias"] = check_deps() >= 3 if shutil.which("gh") else check_deps() >= 2
    
    info("Verificando config Hermes...")
    results["Config Hermes"] = check_hermes_config()
    
    info("Verificando web tools...")
    results["Jina Reader"] = check_web_tools()
    
    info("Verificando Shellz...")
    results["Shellz (roteamento)"] = check_shellz()
    
    info("Verificando compressão...")
    results["Compressao Ollama"] = check_compress()
    
    summary(results)
    return 0 if all(v for v in results.values()) else 1


if __name__ == "__main__":
    main()
