#!/usr/bin/env python3
"""read_url.py — Le qualquer URL via Jina Reader e retorna markdown limpo.

Uso:
    python read_url.py URL                  → conteudo completo
    python read_url.py URL --max 3000       → primeiros 3000 chars
    python read_url.py URL --json           → JSON com metadados

Zero servidor. Zero background. Chama via terminal quando precisar.
"""
import json
import sys
import urllib.request
import urllib.error

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
TIMEOUT = 30


def read_url(url: str, max_chars: int = 0) -> dict:
    """Le uma URL via Jina Reader.

    Args:
        url: URL para ler
        max_chars: Se > 0, trunca o conteudo

    Returns:
        Dict com status, url, content, chars
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    jina_url = f"https://r.jina.ai/{url}"
    req = urllib.request.Request(
        jina_url,
        headers={
            "User-Agent": UA,
            "Accept": "text/plain",
            "X-With-Links-Summary": "true",  # Jina inclui resumo dos links
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            content = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return {"status": "error", "error": f"HTTP {e.code}: {e.reason}", "url": url}
    except urllib.error.URLError as e:
        return {"status": "error", "error": f"URL error: {e.reason}", "url": url}
    except Exception as e:
        return {"status": "error", "error": str(e), "url": url}

    chars = len(content)
    if max_chars > 0 and chars > max_chars:
        content = content[:max_chars] + f"\n\n[... truncado, {chars} chars original]"

    return {
        "status": "ok",
        "url": url,
        "chars": chars,
        "content": content,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Le qualquer URL via Jina Reader")
    parser.add_argument("url", help="URL para ler")
    parser.add_argument("--max", type=int, default=0, help="Max chars (0 = completo)")
    parser.add_argument("--json", action="store_true", help="Saida JSON")

    args = parser.parse_args()
    result = read_url(args.url, args.max)

    if args.json:
        if result["status"] == "ok":
            result["content"] = result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"]
        print(json.dumps(result, ensure_ascii=False))
    else:
        if result["status"] == "error":
            print(f"Erro: {result['error']}", file=sys.stderr)
            return 1
        print(result["content"])

    return 0


if __name__ == "__main__":
    main()
