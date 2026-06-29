#!/usr/bin/env python3
"""Headroom Proxy Custom v2 — compressao de contexto + SSE streaming.
Proxy OpenAI-compativel: intercepta chamadas ao LLM, comprime o contexto, encaminha.

Correcoes:
- ThreadingHTTPServer para concorrencia
- Stripa Transfer-Encoding do upstream (urlopen ja decodificou)
- Suporte a SSE streaming
- Contagem real de tokens comprimidos

Uso:
  python headroom_proxy.py --port 8787 --upstream https://api.deepseek.com
"""

import json
import os
import argparse
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

PORT = int(os.environ.get("HEADROOM_PORT", "8787"))
UPSTREAM = os.environ.get("HEADROOM_UPSTREAM", "https://api.deepseek.com")
TIMEOUT = int(os.environ.get("HEADROOM_TIMEOUT", "120"))

HAS_HEADROOM = False
try:
    from headroom import compress, count_tokens_messages
    HAS_HEADROOM = True
except ImportError:
    pass

STATS = {"requests": 0, "tokens_before": 0, "tokens_after": 0}
STATS_LOCK = threading.Lock()

# Headers do upstream que NAO repassamos ao cliente
NO_FORWARD = {"transfer-encoding", "content-length", "connection"}


class HeadroomProxyHandler(BaseHTTPRequestHandler):
    """Proxy HTTP com compressao de contexto e SSE streaming."""

    def do_GET(self):
        if self.path == "/health":
            return self._json(200, {"status": "ok", "headroom": HAS_HEADROOM, **STATS})
        elif self.path == "/v1/models":
            return self._proxy_request()
        self._json(404, {"error": "not found"})

    def do_POST(self):
        self._proxy_request()

    def log_message(self, *a):
        pass

    # ── Core ─────────────────────────────────────

    def _proxy_request(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b""

        is_stream = False
        data = None
        if body:
            try:
                data = json.loads(body)
                is_stream = data.get("stream", False)
            except Exception:
                pass

        # Comprimir contexto (apenas non-streaming)
        if body and HAS_HEADROOM and not is_stream and data and data.get("messages"):
            try:
                msgs = data["messages"]
                orig = count_tokens_messages(msgs) if callable(count_tokens_messages) else 0
                result = compress(msgs)
                compressed = (
                    getattr(result, "compressed_messages", None)
                    or (result if isinstance(result, dict) and "compressed_messages" in result else None)
                )
                if compressed:
                    data["messages"] = compressed
                    body = json.dumps(data).encode()
                    newc = count_tokens_messages(compressed) if callable(count_tokens_messages) else 0
                    with STATS_LOCK:
                        STATS["requests"] += 1
                        STATS["tokens_before"] += int(orig) if orig else 0
                        STATS["tokens_after"] += int(newc) if newc else 0
            except Exception:
                pass

        # Encaminhar
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ("host", "transfer-encoding", "content-length", "connection")}
        req = Request(UPSTREAM + self.path, data=body, method=self.command, headers=headers)

        try:
            resp = urlopen(req, timeout=TIMEOUT)
            if is_stream:
                self._proxy_stream(resp)
            else:
                self._proxy_normal(resp)
        except URLError as e:
            self._json(502, {"error": str(e.reason)})
        except Exception as e:
            self._json(502, {"error": str(e)})

    # ── Normal (non-streaming) ───────────────────

    def _proxy_normal(self, resp):
        body = resp.read()
        self.send_response(resp.status)
        for k, v in resp.headers.items():
            if k.lower() not in NO_FORWARD:
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── Streaming (SSE) ──────────────────────────

    def _proxy_stream(self, resp):
        self.send_response(resp.status)
        for k, v in resp.headers.items():
            if k.lower() not in NO_FORWARD:
                self.send_header(k, v)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.end_headers()
        try:
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            resp.close()

    # ── JSON helper ──────────────────────────────

    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=PORT)
    p.add_argument("--upstream", type=str, default=UPSTREAM)
    args = p.parse_args()

    if not HAS_HEADROOM:
        print("⚠️  headroom nao disponivel — modo pass-through")
    else:
        print(f"✅ headroom-ai v{getattr(__import__('headroom'), '__version__', '?')}")

    server = ThreadingHTTPServer(("0.0.0.0", args.port), HeadroomProxyHandler)
    print(f"\n🚀 Headroom Proxy v2 em http://0.0.0.0:{args.port}")
    print(f"   Upstream: {args.upstream}")
    print(f"   Timeout: {TIMEOUT}s")
    print(f"   Stream:  ✅ suportado")
    print(f"   Compress: {'✅' if HAS_HEADROOM else '⚠️ pass-through'}")
    print(f"\n   Hermes:  model.base_url = http://localhost:{args.port}/v1")
    print(f"   Saude:   http://localhost:{args.port}/health")
    print(f"\n   Rollback: git checkout headroom-v0-original -- headroom_proxy.py\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        s = STATS
        saved = s["tokens_before"] - s["tokens_after"]
        pct = (saved / s["tokens_before"] * 100) if s["tokens_before"] else 0
        print(f"\n📊 {s['requests']} req | {s['tokens_before']}→{s['tokens_after']} tok ({pct:.1f}%)")
        server.server_close()


if __name__ == "__main__":
    main()
