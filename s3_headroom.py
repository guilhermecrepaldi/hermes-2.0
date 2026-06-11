#!/usr/bin/env python3
"""
S3 Headroom — Context Optimization Layer para o Workbench Hermes
Inspirado no headroom-ai: compressão de contexto, importação de projetos,
busca de soluções. Tudo Python puro (zero Rust), roda no Windows.

Funcionalidades:
1. project_load(path)  → Importa QUALQUER projeto git para contexto do S3
2. context_compress()  → Comprime tool outputs antes do LLM (economia 50-90%)
3. solution_search()   → Busca soluções no projeto + web
4. project_map()       → Mapa estrutural do projeto para decisões do S3
"""
import os
import re
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter

# ══════════════════════════════════════════════════════════════
# 1. PROJECT LOAD — Importa qualquer projeto git
# ══════════════════════════════════════════════════════════════

def project_load(path_or_url: str, target_dir: str = None) -> dict:
    """
    Importa um projeto local ou remoto (git).
    Retorna um resumo estruturado para consumo do S3.
    
    Args:
        path_or_url: Caminho local OU URL git (https://github.com/user/repo)
        target_dir: Onde clonar (se URL). Default: ~/hermes-projects/<repo-name>
    
    Returns:
        Dict com: estrutura, linguagens, arquivos-chave, stats
    """
    result = {
        "status": "pending",
        "path": None,
        "name": None,
        "language": None,
        "files": 0,
        "dirs": 0,
        "lines": 0,
        "key_files": [],
        "dependencies": [],
        "error": None,
    }
    
    # Detect if URL or local path
    is_url = path_or_url.startswith(("http://", "https://", "git@"))
    
    if is_url:
        # Clone remote repo
        repo_name = path_or_url.rstrip("/").split("/")[-1].replace(".git", "")
        if target_dir is None:
            target_dir = os.path.expanduser(f"~/hermes-projects/{repo_name}")
        
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", path_or_url, target_dir],
                capture_output=True, text=True, timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            )
            result["path"] = target_dir
            result["name"] = repo_name
            result["status"] = "cloned"
        except Exception as e:
            result["status"] = "error"
            result["error"] = f"Falha ao clonar: {e}"
            return result
    else:
        # Use local path
        p = Path(path_or_url)
        if not p.exists():
            result["status"] = "error"
            result["error"] = f"Caminho nao existe: {path_or_url}"
            return result
        result["path"] = str(p.resolve())
        result["name"] = p.name
        result["status"] = "local"
    
    # Analyze project structure
    project_path = Path(result["path"])
    
    # Count files and extensions
    extensions = Counter()
    total_lines = 0
    total_files = 0
    total_dirs = 0
    key_files = []
    
    IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv',
                   '.tox', 'dist', 'build', '.next', '.nuxt', 'target',
                   '.idea', '.vscode', '.DS_Store', '*.pyc', '.gitkeep'}
    
    for root, dirs, files in os.walk(project_path):
        # Skip ignored dirs
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        total_dirs += 1
        
        for f in files:
            if f.startswith('.') and f not in {'.env.example', '.gitignore', '.dockerignore'}:
                continue
            total_files += 1
            
            ext = Path(f).suffix.lower()
            if ext:
                extensions[ext] += 1
            
            # Count lines for text files
            fpath = Path(root) / f
            try:
                text_exts = {'.py', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java',
                            '.c', '.cpp', '.h', '.hpp', '.cs', '.rb', '.php', '.swift',
                            '.kt', '.scala', '.clj', '.ex', '.exs', '.html', '.css',
                            '.scss', '.less', '.md', '.rst', '.txt', '.json', '.yaml',
                            '.yml', '.toml', '.cfg', '.ini', '.env.example', '.gitignore',
                            '.dockerignore', '.sql', '.r', '.m', '.mm', '.vue', '.svelte'}
                if ext in text_exts and fpath.stat().st_size < 500000:
                    lines = len(fpath.read_text(encoding='utf-8', errors='ignore').splitlines())
                    total_lines += lines
                    
                    # Identify key files
                    if f in {'README.md', 'index.md', 'setup.py', 'setup.cfg',
                             'pyproject.toml', 'package.json', 'Cargo.toml',
                             'go.mod', 'Gemfile', 'Pipfile', 'requirements.txt',
                             'Makefile', 'Dockerfile', 'docker-compose.yml',
                             '.env.example', '.gitignore', 'main.py', 'app.py',
                             'index.js', 'cli.py', '__init__.py', 'config.py'}:
                        key_files.append({
                            "path": str(fpath.relative_to(project_path)),
                            "lines": lines,
                            "type": ext,
                        })
                    
                    # Collect dependencies from key config files
                    if f == 'requirements.txt':
                        result["dependencies"].append({
                            "file": "requirements.txt",
                            "count": lines,
                        })
                    elif f == 'package.json':
                        try:
                            pkg = json.loads(fpath.read_text(encoding='utf-8', errors='ignore'))
                            deps = list(pkg.get('dependencies', {}).keys()) + list(pkg.get('devDependencies', {}).keys())
                            result["dependencies"].append({
                                "file": "package.json",
                                "count": len(deps),
                                "top": deps[:10],
                            })
                        except: pass
                    elif f == 'pyproject.toml':
                        content = fpath.read_text(encoding='utf-8', errors='ignore')
                        deps_count = content.count('"') // 2  # rough estimate
                        result["dependencies"].append({
                            "file": "pyproject.toml",
                            "count": deps_count,
                        })
            except: pass
    
    result["files"] = total_files
    result["dirs"] = total_dirs
    result["lines"] = total_lines
    
    # Detect main language
    lang_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.jsx': 'React JSX', '.tsx': 'React TSX', '.rs': 'Rust',
        '.go': 'Go', '.java': 'Java', '.c': 'C', '.cpp': 'C++',
        '.cs': 'C#', '.rb': 'Ruby', '.php': 'PHP', '.swift': 'Swift',
        '.kt': 'Kotlin', '.html': 'HTML', '.css': 'CSS',
        '.vue': 'Vue', '.svelte': 'Svelte',
    }
    
    if extensions:
        main_ext = extensions.most_common(1)[0][0]
        result["language"] = lang_map.get(main_ext, main_ext)
    
    # Top 5 extensions
    result["top_extensions"] = [
        {"ext": lang_map.get(ext, ext), "files": count}
        for ext, count in extensions.most_common(5)
    ]
    
    result["key_files"] = key_files[:10]  # top 10 key files
    
    return result


# ══════════════════════════════════════════════════════════════
# 2. CONTEXT COMPRESS — Economia de tokens
# ══════════════════════════════════════════════════════════════

def context_compress(text: str, max_chars: int = 3000) -> str:
    """
    Comprime texto para consumo do LLM:
    - Remove linhas重复/redundantes
    - Mantém apenas estrutura + pontos-chave
    - Ideal para tool outputs longos
    
    Args:
        text: Texto original (ex: tool output, log, arquivo)
        max_chars: Limite de compressão (default: 3000)
    
    Returns:
        Texto comprimido + metadados de economia
    """
    original_chars = len(text)
    original_lines = text.count('\n') + 1
    
    # Remove linhas em branco repetidas (mantém apenas 1)
    compressed = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove linhas de debug/info repetitivas
    skip_patterns = [
        r'^\s*(DEBUG|TRACE|INFO):.*$',  # logs verbosos
        r'^\s*-+$',                      # separadores
        r'^\s*#+\s*$',                   # comentários vazios
        r'^\s*$',                        # linhas em branco
    ]
    lines = compressed.split('\n')
    filtered = []
    for line in lines:
        if any(re.match(p, line) for p in skip_patterns):
            continue
        filtered.append(line)
    
    compressed = '\n'.join(filtered)
    
    # If still too long, keep first N + last N chars
    if len(compressed) > max_chars:
        half = max_chars // 2
        compressed = (compressed[:half] + 
                     f"\n\n[... TRUNCATED: {len(compressed) - max_chars} chars removidos ...]\n\n" +
                     compressed[-half:])
    
    compressed_chars = len(compressed)
    savings = original_chars - compressed_chars
    savings_pct = round((savings / original_chars) * 100) if original_chars > 0 else 0
    
    return (
        f"📦 Compressao: {original_chars} → {compressed_chars} chars "
        f"(-{savings_pct}%, economia de ~{savings_pct // 4 * 1000} tokens)\n"
        f"{'='*60}\n"
        f"{compressed}"
    )


# ══════════════════════════════════════════════════════════════
# 3. SOLUTION SEARCH — Busca de soluções no projeto
# ══════════════════════════════════════════════════════════════

def solution_search(project_path: str, query: str, max_results: int = 5) -> list:
    """
    Busca soluções dentro de um projeto usando ripgrep/grep.
    Retorna trechos de código relevantes para a query.
    
    Args:
        project_path: Caminho do projeto
        query: O que procurar (ex: "funcao de autenticacao", "error handling")
        max_results: Máximo de resultados
    
    Returns:
        Lista de {arquivo, linha, trecho, relevancia}
    """
    results = []
    
    # Try ripgrep first (faster), fallback to grep
    grep_cmd = None
    for cmd in ['rg', 'grep', 'findstr']:
        if shutil.which(cmd):
            grep_cmd = cmd
            break
    
    if not grep_cmd:
        return [{"error": "Nenhuma ferramenta de busca encontrada (rg/grep/findstr)"}]
    
    # Split query into keywords
    keywords = query.lower().split()
    if not keywords:
        return []
    
    # Build grep pattern
    if grep_cmd == 'rg':
        pattern = '|'.join(keywords)
        try:
            r = subprocess.run(
                ['rg', '-n', '--no-heading', '-i', pattern, project_path,
                 '--type-add', 'code:*.py,*.js,*.ts,*.jsx,*.tsx,*.rs,*.go,*.java,*.c,*.cpp,*.rb,*.php',
                 '-t', 'code', '-g', '!.git/', '-g', '!node_modules/', '-g', '!__pycache__/',
                 '-g', '!.venv/', '-g', '!venv/',
                 '-m', '3', '--max-count', str(max_results * 3)],
                capture_output=True, text=True, timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            )
            output = r.stdout
        except: output = ""
    elif grep_cmd == 'grep':
        try:
            r = subprocess.run(
                ['grep', '-rn', '-i', '-l'] + keywords +
                ['--include=*.py', '--include=*.js', '--include=*.ts',
                 '--exclude-dir=.git', '--exclude-dir=node_modules',
                 project_path],
                capture_output=True, text=True, timeout=30,
            )
            output = r.stdout
        except: output = ""
    else:  # findstr (Windows)
        try:
            r = subprocess.run(
                ['findstr', '/S', '/I', '/M', query, 
                 f'{project_path}\\*.py', f'{project_path}\\*.js', f'{project_path}\\*.ts'],
                capture_output=True, text=True, timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            output = r.stdout
        except: output = ""
    
    # Parse results
    for line in output.split('\n')[:max_results * 3]:
        line = line.strip()
        if not line:
            continue
        
        # Format: filename:lineno:content
        if grep_cmd == 'findstr':
            parts = line.split(':', 1)
        else:
            parts = line.split(':', 2)
        
        if len(parts) >= 2:
            filepath = parts[0]
            try:
                lineno = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            except: lineno = 0
            content = parts[-1] if len(parts) > 2 else ""
            
            # Calculate relevance (keyword match count)
            content_lower = content.lower()
            relevance = sum(1 for kw in keywords if kw in content_lower)
            
            results.append({
                "file": filepath,
                "line": lineno,
                "snippet": content.strip()[:150],
                "relevance": relevance,
            })
    
    # Sort by relevance, deduplicate by file
    seen = set()
    unique = []
    for r in sorted(results, key=lambda x: -x['relevance']):
        if r['file'] not in seen:
            seen.add(r['file'])
            unique.append(r)
    
    return unique[:max_results]


# ══════════════════════════════════════════════════════════════
# 4. PROJECT MAP — Mapa estrutural para S3 tomar decisões
# ══════════════════════════════════════════════════════════════

def project_map(project_path: str, max_depth: int = 3) -> str:
    """
    Gera um mapa estrutural do projeto para o S3 entender rapidamente.
    Similar a 'tree' mas filtrando arquivos não relevantes.
    
    Args:
        project_path: Caminho do projeto
        max_depth: Profundidade máxima da árvore
    
    Returns:
        String formatada com a árvore + estatísticas
    """
    root = Path(project_path)
    if not root.exists():
        return f"Erro: {project_path} nao existe"
    
    IGNORE = {'.git', '__pycache__', 'node_modules', '.venv', 'venv',
              '.tox', 'dist', 'build', '.next', '.nuxt', 'target',
              '.idea', '.vscode', '.DS_Store', '*.pyc'}
    
    tree_lines = []
    
    def _walk(path: Path, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            return
        try:
            entries = sorted([e for e in path.iterdir() if e.name not in IGNORE and not e.name.startswith('.')],
                            key=lambda x: (not x.is_dir(), x.name.lower()))
        except: return
        
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            
            if entry.is_dir():
                tree_lines.append(f"{prefix}{connector}{entry.name}/")
                extension = "    " if is_last else "│   "
                _walk(entry, prefix + extension, depth + 1)
            else:
                size = entry.stat().st_size
                size_str = f"({size:,} bytes)" if size < 1024 else f"({size//1024} KB)" if size < 1024*1024 else f"({size//1024//1024} MB)"
                tree_lines.append(f"{prefix}{connector}{entry.name} {size_str}")
    
    tree_lines.append(f"{root.name}/")
    _walk(root)
    
    stats = project_load(project_path)
    
    return (
        f"📂 PROJETO: {root.name}\n"
        f"{'='*50}\n"
        f"Linguagem principal: {stats.get('language', 'N/A')}\n"
        f"Arquivos: {stats['files']} | Pastas: {stats['dirs']} | Linhas: {stats['lines']:,}\n"
        f"Dependencias: {len(stats.get('dependencies', []))} arquivos de config\n"
        f"{'='*50}\n"
        f"\n"
        f"{chr(10).join(tree_lines)}"
    )


# ══════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python s3_headroom.py <comando> [args]")
        print("")
        print("Comandos:")
        print("  load <path|url>      Importa projeto (local ou git)")
        print("  compress <texto>     Comprime texto para LLM")
        print("  search <path> <q>    Busca solucao no projeto")
        print("  map <path>           Mapa estrutural do projeto")
        print("")
        print("Exemplos:")
        print("  python s3_headroom.py load D:\\meu-projeto")
        print("  python s3_headroom.py load https://github.com/user/repo")
        print('  python s3_headroom.py compress "texto longo..."')
        print('  python s3_headroom.py search D:\\projeto "auth login"')
        print("  python s3_headroom.py map D:\\projeto")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "load" and len(sys.argv) >= 3:
        result = project_load(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "compress" and len(sys.argv) >= 3:
        print(context_compress(sys.argv[2]))
    
    elif cmd == "search" and len(sys.argv) >= 4:
        results = solution_search(sys.argv[2], sys.argv[3])
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif cmd == "map" and len(sys.argv) >= 3:
        print(project_map(sys.argv[2]))
    
    else:
        print(f"Comando desconhecido: {cmd}")


if __name__ == "__main__":
    main()
