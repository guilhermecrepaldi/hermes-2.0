#!/usr/bin/env python3
"""
Headroom Cache Proxy — lightweight caching layer for DeepSeek API.
Python stdlib only (http.server, urllib, sqlite3).

Routes: POST /v1/chat/completions → cache check → DeepSeek API
Cache: SQLite, keyed by SHA256 of request body JSON.
Streaming: NOT cached (pass-through).
Non-streaming: cached indefinitely (TTL opcional futuramente).

Usage:
    python headroom_cache.py [--port 8787] [--cache-dir ~/.hermes/headroom_cache]
"""

from __future__ import annotations

import hashlib
import http.server
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from typing import Any

# ── Config ────────────────────────────────────────────────────
DEFAULT_PORT = 8787
DEEPSEEK_BASE = "https://api.deepseek.com"
HOME_DIR = os.path.expanduser("~")
DEFAULT_CACHE_DIR = os.path.join(HOME_DIR, ".hermes", "headroom_cache")
CACHE_DB = "cache.db"


def _load_deepseek_key() -> str:
    """Lê DEEPSEEK_API_KEY do .env do Hermes ou variável de ambiente."""
    env_path = os.path.join(HOME_DIR, "AppData", "Local", "hermes", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DEEPSEEK_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("\"'")
    return os.environ.get("DEEPSEEK_API_KEY", "")


DEEPSEEK_API_KEY = _load_deepseek_key()


# ── Cache SQLite ──────────────────────────────────────────────
class ResponseCache:
    """SQLite-backed cache for API responses."""

    def __init__(self, cache_dir: str):
        os.makedirs(cache_dir, exist_ok=True)
        self.db_path = os.path.join(cache_dir, CACHE_DB)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    response TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    hits INTEGER DEFAULT 1,
                    tokens INTEGER DEFAULT 0
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON cache(key)")
            conn.commit()

    def _hash(self, body: bytes) -> str:
        return hashlib.sha256(body).hexdigest()

    def get(self, body: bytes) -> dict[str, Any] | None:
        key = self._hash(body)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT response, hits FROM cache WHERE key = ?", (key,)
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE cache SET hits = hits + 1 WHERE key = ?", (key,)
                )
                conn.commit()
                return json.loads(row["response"])
        return None

    def set(self, body: bytes, response: dict[str, Any]) -> None:
        key = self._hash(body)
        tokens = 0
        if "usage" in response:
            tokens = response["usage"].get("total_tokens", 0)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache (key, response, created_at, hits, tokens)
                VALUES (?, ?, ?, 1, ?)
                """,
                (key, json.dumps(response), time.time(), tokens),
            )
            conn.commit()

    def stats(self) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) as entries, COALESCE(SUM(hits),0) as total_hits, "
                "COALESCE(SUM(tokens),0) as total_tokens FROM cache"
            ).fetchone()
            return {
                "entries": row[0],
                "total_hits": row[1],
                "total_tokens": row[2],
            }

    def clear(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
            conn.execute("DELETE FROM cache")
            conn.commit()
        return count


# ── Proxy Server ──────────────────────────────────────────────
class HeadroomProxyHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the caching proxy."""

    cache: ResponseCache | None = None
    deepseek_key: str = ""
    server_start: float = time.time()

    def log_message(self, format: str, *args: Any) -> None:
        if os.environ.get("HEADROOM_VERBOSE"):
            super().log_message(format, *args)

    def _send_json(self, status: int, data: dict[str, Any]) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _forward_to_deepseek(
        self, body: bytes, is_stream: bool = False
    ) -> dict[str, Any] | None:
        """Forward request to DeepSeek API."""
        url = f"{DEEPSEEK_BASE}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_key}",
        }
        if is_stream:
            headers["Accept"] = "text/event-stream"
        else:
            headers["Accept"] = "application/json"

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read()
                if is_stream:
                    # Streaming: write raw SSE back to client
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(raw)
                    self.wfile.flush()
                    return None
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            return {
                "error": {
                    "message": f"DeepSeek API error {e.code}: {error_body}",
                    "type": "proxy_error",
                    "code": e.code,
                }
            }
        except urllib.error.URLError as e:
            return {
                "error": {
                    "message": f"DeepSeek connection error: {e.reason}",
                    "type": "proxy_error",
                    "code": 503,
                }
            }
        except Exception as e:
            return {
                "error": {
                    "message": f"Proxy error: {str(e)}",
                    "type": "proxy_error",
                    "code": 500,
                }
            }

    def _handle_chat_completions(self, body: bytes) -> None:
        """Handle POST /v1/chat/completions with caching."""
        try:
            req_data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": {"message": "Invalid JSON", "type": "invalid_request"}})
            return

        is_stream = req_data.get("stream", False)

        if is_stream:
            # Streaming: forward directly, no caching
            self._forward_to_deepseek(body, is_stream=True)
            return

        # Non-streaming: check cache first
        cached = self.cache.get(body) if self.cache else None
        if cached:
            cached["_cache"] = "HIT"
            self._send_json(200, cached)
            return

        # Miss: forward to DeepSeek
        result = self._forward_to_deepseek(body)
        if not result:
            self._send_json(502, {"error": {"message": "Empty response from upstream", "type": "proxy_error"}})
            return

        if "error" in result:
            code = result["error"].get("code", 500)
            self._send_json(code, result)
            return

        # Cache successful response
        if self.cache:
            self.cache.set(body, result)
        result["_cache"] = "MISS"
        self._send_json(200, result)

    def _handle_models(self) -> None:
        """Handle GET /v1/models — returns DeepSeek model list."""
        try:
            req = urllib.request.Request(
                f"{DEEPSEEK_BASE}/v1/models",
                headers={"Authorization": f"Bearer {self.deepseek_key}"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                self._send_json(200, data)
        except Exception:
            self._send_json(
                200,
                {
                    "object": "list",
                    "data": [
                        {"id": "deepseek-v4-flash", "object": "model"},
                        {"id": "deepseek-chat", "object": "model"},
                        {"id": "deepseek-reasoner", "object": "model"},
                    ],
                },
            )

    def do_GET(self):
        if self.path in ("/v1/models", "/models"):
            self._handle_models()
        elif self.path == "/health":
            self._send_json(200, {"status": "ok", "uptime": time.time() - self.server_start})
        else:
            self._send_json(404, {"error": {"message": "Not found", "type": "not_found"}})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        if self.path == "/v1/chat/completions":
            self._handle_chat_completions(body)
        else:
            self._send_json(404, {"error": {"message": "Not found", "type": "not_found"}})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()


def run_server(port: int = DEFAULT_PORT, cache_dir: str | None = None) -> None:
    """Start the headroom caching proxy server."""
    if not DEEPSEEK_API_KEY:
        print("❌ DEEPSEEK_API_KEY não encontrada. Configure no .env do Hermes.")
        sys.exit(1)

    if cache_dir is None:
        cache_dir = DEFAULT_CACHE_DIR

    cache = ResponseCache(cache_dir)
    HeadroomProxyHandler.cache = cache
    HeadroomProxyHandler.deepseek_key = DEEPSEEK_API_KEY
    HeadroomProxyHandler.server_start = time.time()

    stats = cache.stats()
    print(f"🧠 Headroom Cache Proxy")
    print(f"   Porta:     {port}")
    print(f"   Cache DB:  {cache.db_path}")
    print(f"   Entradas:  {stats['entries']}")
    print(f"   Hits:      {stats['total_hits']}")
    print(f"   Tokens:    {stats['total_tokens']}")
    print(f"   Upstream:  {DEEPSEEK_BASE}")
    print(f"   ✅ Pronto em http://127.0.0.1:{port}/v1")

    server = http.server.HTTPServer(("127.0.0.1", port), HeadroomProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Headroom desligado.")
        server.server_close()


if __name__ == "__main__":
    port = DEFAULT_PORT
    cache_dir = DEFAULT_CACHE_DIR

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
        elif arg == "--cache-dir" and i + 1 < len(args):
            cache_dir = args[i + 1]
        elif arg == "--verbose":
            os.environ["HEADROOM_VERBOSE"] = "1"

    run_server(port=port, cache_dir=cache_dir)
