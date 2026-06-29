#!/usr/bin/env python3
"""Headroom Proxy Custom — compressao de contexto inline para Hermes.
Nao precisa de Rust core. Usa a biblioteca headroom Python diretamente.

Proxy: intercepta chamadas ao LLM, comprime o contexto, encaminha.
"""
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

# ─── CONFIG ────────────────────────────────────
PORT = int(os.environ.get("HEADROOM_PORT", "8787"))
UPSTREAM = os.environ.get("HEADROOM_UPSTREAM", "https://api.deepseek.com")
# ───────────────────────────────────────────────

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "watchdog"))
try:
    from headroom_bridge import compress_messages, compress_text
    HAS_HEADROOM = True
except ImportError:
    HAS_HEADROOM = False

STATS = {"requests": 0, "tokens_before": 0, "tokens_after": 0}


class HeadroomProxyHandler(BaseHTTPRequestHandler):
    """Proxy HTTP que comprime contexto antes de encaminhar."""
    
    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "ok", "headroom": HAS_HEADROOM, **STATS})
        elif self.path == "/v1/models":
            self._proxy_request()
        else:
            self._json(404, {"error": "not found"})
    
    def do_POST(self):
        self._proxy_request()
    
    def _proxy_request(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b""
        
        if body:
            try:
                data = json.loads(body)
                messages = data.get("messages", [])
                if messages:
                    result = compress_messages(messages)
                    saved = result.get("tokens_saved", 0)
                    if saved > 0:
                        data["messages"] = result["messages"]
                        STATS["tokens_before"] += result.get("tokens_before", 0)
                        STATS["tokens_after"] += result.get("tokens_after", 0)
                        STATS["requests"] += 1
                        body = json.dumps(data).encode()
            except (json.JSONDecodeError, Exception):
                pass
        
        # Encaminhar para upstream
        url = UPSTREAM + self.path
        req = Request(url, data=body, method=self.command,
                     headers={k: v for k, v in self.headers.items()
                             if k.lower() not in ("host", "content-length")})
        
        try:
            resp = urlopen(req, timeout=30)
            self.send_response(resp.status)
            for k, v in resp.headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.read())
        except URLError as e:
            self._json(502, {"error": str(e.reason)})
    
    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass  # silencia logs do servidor


def main():
    if not HAS_HEADROOM:
        print("ERRO: headroom_bridge nao encontrado")
        sys.exit(1)
    
    server = HTTPServer(("0.0.0.0", PORT), HeadroomProxyHandler)
    print(f"Headroom Proxy rodando em :{PORT}")
    print(f"Upstream: {UPSTREAM}")
    print(f"Use: export DEEPSEEK_BASE_URL=http://localhost:{PORT}/v1")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\nStats: {STATS['requests']} req, "
              f"{STATS['tokens_before']}→{STATS['tokens_after']} tok "
              f"({(1-STATS['tokens_after']/max(STATS['tokens_before'],1))*100:.0f}%)")
        server.server_close()


if __name__ == "__main__":
    main()
