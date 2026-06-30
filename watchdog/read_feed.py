#!/usr/bin/env python3
"""read_feed.py — Le RSS/Atom feeds e retorna os items recentes.

Uso:
    python read_feed.py URL                  → ultimas 5 entradas
    python read_feed.py URL --limit 10       → ultimas 10
    python read_feed.py URL --json           → JSON estruturado

Zero servidor. Zero background. Chama via terminal quando precisar.
"""
import json
import sys
from datetime import datetime

try:
    import feedparser
except ImportError:
    print("feedparser nao instalado. Instale: pip install feedparser", file=sys.stderr)
    sys.exit(1)


def read_feed(url: str, limit: int = 5) -> dict:
    """Le um RSS/Atom feed.

    Args:
        url: URL do feed
        limit: Max de entradas

    Returns:
        Dict com feed info + entries
    """
    parsed = feedparser.parse(url)

    if parsed.bozo and not parsed.entries:
        return {
            "status": "error",
            "error": str(parsed.bozo_exception) if hasattr(parsed, 'bozo_exception') else "Falha ao parsear feed",
            "url": url,
        }

    feed_info = {
        "title": parsed.feed.get("title", ""),
        "link": parsed.feed.get("link", ""),
        "description": parsed.feed.get("subtitle", "") or parsed.feed.get("description", ""),
        "updated": parsed.feed.get("updated", ""),
    }

    entries = []
    for entry in parsed.entries[:limit]:
        e = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", "") or entry.get("updated", ""),
            "summary": entry.get("summary", "")[:500] if entry.get("summary") else "",
        }
        entries.append(e)

    return {
        "status": "ok",
        "url": url,
        "feed": feed_info,
        "total_entries": len(parsed.entries),
        "entries": entries,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Le RSS/Atom feeds")
    parser.add_argument("url", help="URL do feed RSS/Atom")
    parser.add_argument("--limit", type=int, default=5, help="Max entradas (default: 5)")
    parser.add_argument("--json", action="store_true", help="Saida JSON")

    args = parser.parse_args()
    result = read_feed(args.url, args.limit)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if result["status"] == "error":
        print(f"Erro: {result['error']}", file=sys.stderr)
        return 1

    feed = result["feed"]
    print(f"📡 {feed['title']}")
    print(f"   {feed['link']}")
    print(f"   {result['total_entries']} entries | ultimas {len(result['entries'])}:")
    print()

    for i, entry in enumerate(result["entries"], 1):
        print(f"{i}. {entry['title']}")
        print(f"   {entry['link']}")
        if entry.get("published"):
            print(f"   [{entry['published']}]")
        if entry.get("summary"):
            s = entry["summary"].replace("\n", " ").strip()[:200]
            print(f"   {s}...")
        print()

    return 0


if __name__ == "__main__":
    main()
