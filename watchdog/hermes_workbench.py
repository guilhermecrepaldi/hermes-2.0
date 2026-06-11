#!/usr/bin/env python3
"""
Hermes Workbench — CLI Unificada
Todas as ferramentas do Workbench Hermes em um único comando.
Uso: hermes-workbench <comando> [args]

Comandos:
  panorama <path>      Panorama completo de qualquer projeto (S3/S2)
  compress <texto>     Comprime tool outputs para economizar tokens
  search <path> <q>    Busca solução em projeto local
  grep <query>         Busca código em 1M+ repos GitHub (grep.app)
  router <tarefa>      Classifica tarefa em S1/S2/S3
  status               Status do watchdog + shells
  help                 Mostra ajuda completa
"""
import sys
import os
import json
from datetime import datetime

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cmd_panorama(args):
    """Panorama COMPLETO de qualquer projeto para S3/S2 tomarem decisoes."""
    if not args:
        print("Uso: hermes-workbench panorama <path>")
        return 1
    
    project_path = args[0]
    from s3_headroom import project_load, project_map, solution_search
    
    print("=" * 60)
    print(f"🧠 S3/S2 PANORAMA — {os.path.basename(project_path)}")
    print("=" * 60)
    
    # 1. Project load (estrutura + estatisticas)
    print("\n📊 ESTRUTURA DO PROJETO")
    print("-" * 40)
    info = project_load(project_path)
    print(f"  Linguagem: {info.get('language', 'N/A')}")
    print(f"  Arquivos:  {info['files']}")
    print(f"  Pastas:    {info['dirs']}")
    print(f"  Linhas:    {info['lines']:,}")
    print(f"  Status:    {info['status']}")
    if info.get('top_extensions'):
        exts = [f"{e['ext']} ({e['files']})" for e in info['top_extensions'][:3]]
        print(f"  Extensoes: {', '.join(exts)}")
    if info.get('key_files'):
        print(f"  Arquivos-chave: {len(info['key_files'])} encontrados")
    
    # 2. Project map (arvore)
    print("\n🗺️  ÁRVORE DO PROJETO")
    print("-" * 40)
    tree = project_map(project_path, max_depth=2)
    tree_lines = tree.split('\n')
    for line in tree_lines[:25]:
        print(f"  {line}")
    if len(tree_lines) > 25:
        print(f"  ... (+{len(tree_lines)-25} linhas)")

    # 3. Key files analysis
    print("\n📄 ARQUIVOS-CHAVE")
    print("-" * 40)
    for kf in info.get('key_files', [])[:5]:
        print(f"  📄 {kf['path']} ({kf['lines']} linhas)")
    
    # 4. Dependencies
    if info.get('dependencies'):
        print(f"\n📦 DEPENDENCIAS ({len(info['dependencies'])} arquivos de config)")
    
    print("\n✅ Panorama completo para S3/S2")
    return 0


def cmd_compress(args):
    """Comprime texto para economizar tokens."""
    if not args:
        print("Uso: hermes-workbench compress <texto>")
        return 1
    from s3_headroom import context_compress
    print(context_compress(" ".join(args)))
    return 0


def cmd_search(args):
    """Busca solucao em projeto local."""
    if len(args) < 2:
        print("Uso: hermes-workbench search <path> <query>")
        return 1
    from s3_headroom import solution_search
    results = solution_search(args[0], " ".join(args[1:]))
    for r in results[:5]:
        print(f"  📄 {r['file']}:{r['line']}  [rel:{r['relevance']}]")
        print(f"     {r['snippet'][:100]}")
    return 0


def cmd_grep(args):
    """Busca codigo em 1M+ repos GitHub via grep.app."""
    if not args:
        print("Uso: hermes-workbench grep <query> [--lang L] [--max N]")
        return 1
    
    query = args[0]
    lang = None
    max_results = 5
    
    for i, a in enumerate(args[1:], 1):
        if a == '--lang' and i + 1 < len(args):
            lang = args[i + 1]
        elif a == '--max' and i + 1 < len(args):
            max_results = int(args[i + 1])
    
    # Use browser tool for grep.app (avoids rate limiting)
    print(f"🔍 Buscando '{query}' em 1M+ repos GitHub...")
    print(f"   (use browser_tool directamente para resultados reais)")
    print(f"\nSugestao: browser_navigate('https://grep.app/search?q={query.replace(' ', '+')}')")
    return 0


def cmd_router(args):
    """Classifica tarefa em S1/S2/S3."""
    if not args:
        print("Uso: hermes-workbench router <tarefa>")
        return 1
    from s1_router import classify_task
    result = classify_task(" ".join(args))
    print(f"  Shell:    {result['shell']} ({result['model']})")
    print(f"  Custo:    {result['cost']}")
    print(f"  Motivo:   {result['reason']}")
    print(f"  Scores:   S1={result['score']['S1']}  S2={result['score']['S2']}  S3={result['score']['S3']}")
    return 0


def cmd_status(args):
    """Status do watchdog + shells."""
    import subprocess
    
    def tasklist(name):
        r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH"],
                          capture_output=True, text=True, timeout=10,
                          creationflags=subprocess.CREATE_NO_WINDOW)
        return name in r.stdout.lower()
    
    print("=" * 40)
    print("📊 WORKBENCH STATUS")
    print("=" * 40)
    
    shells = [
        ("S1 (Ollama)", "ollama.exe", "$0,00 🆓"),
        ("S2 (DeepSeek)", None, "~$0.15/M ☁️"),
        ("S3 (deepseek-pro)", None, "~$0.50/M 🧠"),
    ]
    
    for name, proc, cost in shells:
        if proc:
            status = "🟢" if tasklist(proc) else "🔴"
            print(f"  {status} {name:<20} {cost}")
        else:
            print(f"  🟢 {name:<20} {cost} (via API)")
    
    ws = tasklist("wscript.exe")
    pw = tasklist("pythonw.exe")
    print(f"  {'🟢' if ws else '🔴'} Watchdog Guardian     wscript.exe")
    print(f"  {'🟢' if pw else '🔴'} Watchdog (pythonw)    pythonw.exe")
    
    # Check files
    wd = os.path.dirname(os.path.abspath(__file__))
    tools = [
        ("s3_headroom.py", "🧠 S3 Headroom"),
        ("s3_grep.py", "🔍 S3 Grep"),
        ("s1_router.py", "🧭 S1 Router"),
        ("watchdog_hermes.py", "⚙️ Watchdog"),
        ("shellz_menu.bat", "🖥️ Shellz Menu"),
    ]
    print(f"\n  FERRAMENTAS INSTALADAS:")
    for f, name in tools:
        exists = os.path.exists(os.path.join(wd, f))
        print(f"  {'✅' if exists else '❌'} {name:<20} {f}")
    
    return 0


def cmd_help(args):
    """Mostra ajuda completa."""
    print(__doc__)
    print("\nExemplos:")
    print('  hermes-workbench panorama D:\\meu-projeto')
    print('  hermes-workbench compress "texto longo..."')
    print('  hermes-workbench search D:\\projeto "auth login"')
    print('  hermes-workbench grep "api key python" --max 5')
    print('  hermes-workbench router "Criar funcao de autenticacao"')
    print('  hermes-workbench status')
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help', 'help'):
        return cmd_help(sys.argv[2:])
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        'panorama': cmd_panorama,
        'compress': cmd_compress,
        'search': cmd_search,
        'grep': cmd_grep,
        'router': cmd_router,
        'status': cmd_status,
        'help': cmd_help,
    }
    
    if cmd not in commands:
        print(f"Comando desconhecido: {cmd}")
        print("Use 'hermes-workbench help' para ver os comandos disponiveis.")
        return 1
    
    return commands[cmd](args)


if __name__ == "__main__":
    sys.exit(main())
