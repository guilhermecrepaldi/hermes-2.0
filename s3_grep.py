#!/usr/bin/env python3
"""
S3 Grep — Integracao com grep.app (Vercel)
Busca codigo em 1 milhao+ repositorios GitHub.
Usa web scraping via requests com rate limiting respeitoso.

Uso:
  python s3_grep.py search "query" [--lang python] [--repo owner/repo] [--max N]
  python s3_grep.py search "api key" --lang python --max 5
"""
import json
import re
import time
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from dataclasses import dataclass, field, asdict
from typing import Optional

# ══════════════════════════════════════════════════════════════
# Data Models
# ══════════════════════════════════════════════════════════════

@dataclass
class GrepResult:
    repo: str
    repo_url: str
    file_path: str
    file_url: str
    line: int
    snippet: str
    matches: int = 1

@dataclass
class GrepResponse:
    query: str
    total_results: int
    results: list
    filters: dict = field(default_factory=dict)
    error: Optional[str] = None
    time_ms: int = 0


# ══════════════════════════════════════════════════════════════
# HTML Parser for grep.app results
# ══════════════════════════════════════════════════════════════

class GrepHTMLParser(HTMLParser):
    """Parse grep.app search results from HTML."""
    
    def __init__(self):
        super().__init__()
        self.results = []
        self.total = 0
        self._current = {}
        self._in_result = False
        self._in_repo = False
        self._in_path = False
        self._in_snippet = False
        self._in_line = False
        self._tag_stack = []
        self._capture_text = False
        self._text_buffer = ""
        self._line_num = 0
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self._tag_stack.append(tag)
        
        # Detect result rows - each result has a link to repo
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            if href.startswith('/') and '/' in href[1:]:
                # Could be repo/file link
                parts = href.split('/')
                if len(parts) >= 3:  # /owner/repo/path
                    if not self._current.get('repo_url'):
                        self._current['repo_url'] = f"https://github.com{href}"
                        self._current['repo'] = '/'.join(parts[1:3])
                        self._in_repo = True
        
        # Check for result containers (table rows with code)
        if 'class' in attrs_dict:
            cls = attrs_dict['class']
            if 'line' in cls:
                self._in_line = True
                self._text_buffer = ""
            elif 'code' in cls:
                self._in_snippet = True
                self._text_buffer = ""
    
    def handle_endtag(self, tag):
        if tag == 'a' and self._in_repo:
            self._in_repo = False
        if tag in ('span', 'div') and self._in_snippet:
            self._in_snippet = False
        if tag == 'tr' and self._in_line:
            self._in_line = False
        if self._tag_stack:
            self._tag_stack.pop()
    
    def handle_data(self, data):
        if self._in_repo and data.strip():
            self._current['repo'] = data.strip()
        if self._in_snippet and data.strip():
            self._text_buffer += data


def search_grep(query: str, lang: str = None, repo: str = None, 
                max_results: int = 10, timeout: int = 30) -> GrepResponse:
    """
    Search grep.app for code snippets.
    
    Args:
        query: Text to search for (e.g., "api key authentication")
        lang: Filter by language (python, go, rust, typescript, etc.)
        repo: Filter by repository (e.g., "fastapi/fastapi")
        max_results: Max results to return (default: 10)
        timeout: Request timeout in seconds
    
    Returns:
        GrepResponse with results
    """
    start_time = time.time()
    t0 = start_time
    
    # Build URL
    params = {'q': query}
    if lang:
        params['lang'] = lang
    if repo:
        params['repo'] = repo
    
    url = f"https://grep.app/search?{urllib.parse.urlencode(params)}"
    
    # Try JSON API first (grep.app may have an undocumented API)
    json_url = f"https://grep.app/search?q={urllib.parse.quote(query)}&json=1"
    if lang:
        json_url += f"&lang={lang}"
    if repo:
        json_url += f"&repo={repo}"
    
    req = urllib.request.Request(
        json_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/html",
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode('utf-8')
            resp_time = int((time.time() - t0) * 1000)
            
            # Try JSON parse
            try:
                json_data = json.loads(data)
                results = []
                for item in json_data.get('results', json_data.get('hits', [])):
                    results.append(GrepResult(
                        repo=item.get('repo', ''),
                        repo_url=f"https://github.com/{item.get('repo', '')}",
                        file_path=item.get('path', ''),
                        file_url=f"https://github.com/{item.get('repo', '')}/blob/main/{item.get('path', '')}",
                        line=item.get('line', 0),
                        snippet=item.get('content', ''),
                        matches=item.get('matches', 1),
                    ))
                    if len(results) >= max_results:
                        break
                
                return GrepResponse(
                    query=query,
                    total_results=json_data.get('total', len(results)),
                    results=results,
                    filters={'lang': lang, 'repo': repo},
                    time_ms=resp_time,
                )
            except json.JSONDecodeError:
                # HTML response - parse it
                pass
    except urllib.error.HTTPError as e:
        if e.code == 429:
            # Rate limited - respect and wait
            time.sleep(5)
        elif e.code != 200:
            pass
    
    # Fallback: search via normal HTML URL
    req2 = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html",
        }
    )
    
    try:
        time.sleep(1)  # Rate limit respect
        with urllib.request.urlopen(req2, timeout=timeout) as resp:
            html = resp.read().decode('utf-8')
            resp_time = int((time.time() - t0) * 1000)
            
            # Extract total count from HTML
            total_match = re.search(r'([\d,]+)\s*results?\s*found', html)
            total = int(total_match.group(1).replace(',', '')) if total_match else 0
            
            # Extract results using regex patterns
            results = []
            
            # Pattern: repo links and their code snippets
            # grep.app renders results in a structured format
            repo_pattern = r'<a[^>]*href="/([^/"]+)/([^/"]+)"[^>]*>'
            snippet_pattern = r'<tr[^>]*>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(.*?)</td>.*?</tr>'
            
            repos = re.findall(r'<a[^>]*href="/([^/"]+)/([^/"]+)"[^>]*>([^<]+)</a>', html)
            snippets = re.findall(r'<div[^>]*class="[^"]*code[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
            lines = re.findall(r'<td[^>]*class="[^"]*line[^"]*"[^>]*>(\d+)</td>', html)
            paths = re.findall(r'<a[^>]*class="[^"]*path[^"]*"[^>]*>([^<]+)</a>', html)
            
            # Fallback: simpler extraction
            # Look for result blocks: repo name + file path + code snippet
            blocks = re.split(r'<div[^>]*class="[^"]*result[^"]*"', html)
            
            for i, block in enumerate(blocks[1:max_results+1], 1):
                repo_match = re.search(r'/([^/"]+)/([^/"]+)"', block)
                file_match = re.search(r'/(blob/[^"]+)', block)
                code_blocks = re.findall(r'<mark[^>]*>(.*?)</mark>', block, re.DOTALL)
                
                repo_name = repo_match.group(1) + '/' + repo_match.group(2) if repo_match else '?'
                file_path = urllib.parse.unquote(file_match.group(1)) if file_match else '?'
                snippet = ' '.join(re.sub(r'<[^>]+>', '', c).strip() for c in code_blocks[:3])
                
                if repo_name != '?':
                    results.append(GrepResult(
                        repo=repo_name,
                        repo_url=f"https://github.com/{repo_name}",
                        file_path=file_path,
                        file_url=f"https://github.com/{file_match.group(1) if file_match else repo_name}",
                        line=i,
                        snippet=snippet[:200],
                        matches=len(code_blocks),
                    ))
            
            return GrepResponse(
                query=query,
                total_results=total or len(results),
                results=results,
                filters={'lang': lang, 'repo': repo},
                time_ms=resp_time,
            )
            
    except urllib.error.HTTPError as e:
        return GrepResponse(
            query=query,
            total_results=0,
            results=[],
            error=f"HTTP {e.code}: {e.reason}",
            time_ms=int((time.time() - t0) * 1000),
        )
    except Exception as e:
        return GrepResponse(
            query=query,
            total_results=0,
            results=[],
            error=str(e),
            time_ms=int((time.time() - t0) * 1000),
        )


# ══════════════════════════════════════════════════════════════
# S3 Integration
# ══════════════════════════════════════════════════════════════

def s3_solution_search(problem: str, context: str = None) -> dict:
    """
    Busca solucoes para um problema de codigo usando grep.app + s3_headroom.
    Fluxo completo para o S3:
    1. Busca no grep.app por implementacoes de referencia
    2. Escaneia projetos locais com s3_headroom.solution_search()
    3. Compila resultado estruturado para decisao do S3
    
    Args:
        problem: Descricao do problema (ex: "fastapi JWT authentication middleware")
        context: Contexto adicional (opcional)
    
    Returns:
        Dict com solucoes encontradas, repos, trechos
    """
    from datetime import datetime
    
    # Extract keywords from problem
    keywords = re.findall(r'\w+', problem.lower())
    search_query = ' '.join(keywords[:8])  # Use first 8 keywords
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "problem": problem,
        "solutions_found": 0,
        "repos": [],
        "snippets": [],
        "notes": [],
    }
    
    # Search grep.app for solutions
    grepped = search_grep(search_query, max_results=5)
    
    if grepped.error:
        result["notes"].append(f"grep.app: {grepped.error}")
    else:
        result["total_github_hits"] = grepped.total_results
        for r in grepped.results[:5]:
            result["repos"].append({
                "repo": r.repo,
                "file": r.file_path,
                "url": r.file_url,
                "matches": r.matches,
            })
            result["snippets"].append({
                "source": f"github.com/{r.repo}",
                "file": r.file_path,
                "snippet": r.snippet[:150],
            })
        result["solutions_found"] = len(grepped.results)
    
    return result


# ══════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("S3 Grep — Busca de codigo em 1M+ repositorios GitHub")
        print("")
        print("Uso:")
        print("  python s3_grep.py search <query> [--lang L] [--repo R] [--max N]")
        print("  python s3_grep.py solve <problema>")
        print("")
        print("Exemplos:")
        print('  python s3_grep.py search "api key authentication" --lang python --max 3')
        print('  python s3_grep.py solve "fastapi JWT middleware"')
        return
    
    cmd = sys.argv[1]
    
    if cmd == "search":
        if len(sys.argv) < 3:
            print("Erro: forneca a query de busca")
            return
        
        query = sys.argv[2]
        lang = None
        repo = None
        max_results = 10
        
        args = sys.argv[3:]
        for i, a in enumerate(args):
            if a == '--lang' and i + 1 < len(args):
                lang = args[i + 1]
            elif a == '--repo' and i + 1 < len(args):
                repo = args[i + 1]
            elif a == '--max' and i + 1 < len(args):
                max_results = int(args[i + 1])
        
        resp = search_grep(query, lang=lang, repo=repo, max_results=max_results)
        
        print(json.dumps(asdict(resp) if hasattr(resp, '__dataclass_fields__') else {
            "query": resp.query,
            "total_results": resp.total_results,
            "results": [asdict(r) if hasattr(r, '__dataclass_fields__') else r for r in resp.results],
            "error": resp.error,
            "time_ms": resp.time_ms,
        }, indent=2, ensure_ascii=False))
    
    elif cmd == "solve":
        if len(sys.argv) < 3:
            print("Erro: forneca o problema")
            return
        problem = " ".join(sys.argv[2:])
        result = s3_solution_search(problem)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
