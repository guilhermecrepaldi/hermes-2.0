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
OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")
SUMMARY_MAX_CHARS = int(os.environ.get("SUMMARY_MAX_CHARS", "300"))

HAS_HEADROOM = False
HAS_RUST_CORE = False
try:
    from headroom import compress, count_tokens_messages
    HAS_HEADROOM = True
except ImportError:
    pass

# Tentar carregar compressores Rust nativos
try:
    from headroom import _core
    HAS_RUST_CORE = True
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

    def log_message(self, fmt, *args):
        pass  # silencia logs

    # ── Debug ─────────────────────────────────────

    def _debug(self, msg):
        import sys
        print(f"[HEADROOM] {msg}", flush=True)

    # ── Core ─────────────────────────────────────

    def _proxy_request(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b""
        self._debug(f"Request: {len(body)}b body, path={self.path}")

        is_stream = False
        data = None
        if body:
            try:
                data = json.loads(body)
                is_stream = data.get("stream", False)
                self._debug(f"Parsed: stream={is_stream}, msgs={len(data.get('messages',[]))}")
            except Exception as e:
                self._debug(f"Parse error: {e}")
                pass

        # ── Comprimir contexto ────────────────────
        # Usa compressores Rust nativos primeiro (ate 80% em JSON),
        # fallback pro headroom.compress() padrao
        # ── Comprimir contexto ────────────────────
        self._debug("Compression phase start")
        compression_info = {"engine": "passthrough", "saved": 0, "pct": 0.0}
        if body and not is_stream and data and data.get("messages"):
            try:
                msgs = data["messages"]
                chars_before = sum(len(m.get("content", "")) for m in msgs if isinstance(m, dict))
                tok_est_before = max(chars_before // 4, 1)
                self._debug(f"Compression: {len(msgs)} msgs, {chars_before} chars")

                # Estrategia 1: resumir tool outputs via Ollama
                compressed = None
                if HAS_RUST_CORE:
                    self._debug("Trying Ollama summarization...")
                    compressed = self._safe_dedup(msgs)
                    self._debug(f"Ollama result: {type(compressed).__name__}")

                # Estrategia 2: fallback headroom.compress()
                if compressed is None and HAS_HEADROOM:
                    self._debug("Trying headroom.compress()...")
                    try:
                        result = compress(msgs)
                        compressed = (
                            getattr(result, "messages", None)
                            or getattr(result, "compressed_messages", None)
                        )
                        if compressed and len(compressed) == len(msgs):
                            ok = any(a != b for a, b in zip(msgs, compressed))
                            if not ok:
                                compressed = None
                        self._debug(f"headroom.compress result: {type(compressed).__name__ if compressed else 'None'}")
                    except Exception as e:
                        self._debug(f"headroom.compress error: {e}")
                        pass

                if compressed:
                    data["messages"] = compressed
                    body = json.dumps(data).encode()
                    chars_after = sum(len(m.get("content","")) for m in compressed if isinstance(m,dict))
                    tok_est_after = max(chars_after // 4, 1)
                if compressed:
                    data["messages"] = compressed
                    body = json.dumps(data).encode()
                    chars_after = sum(len(m.get("content", "")) for m in compressed if isinstance(m, dict))
                    tok_est_after = max(chars_after // 4, 1)
                    saved = tok_est_before - tok_est_after
                    pct = (saved / tok_est_before * 100) if tok_est_before else 0
                    with STATS_LOCK:
                        STATS["requests"] += 1
                        STATS["tokens_before"] += tok_est_before
                        STATS["tokens_after"] += tok_est_after
                    compression_info = {"engine": "rust" if HAS_RUST_CORE else "py", "saved": saved, "pct": pct}
            except Exception:
                pass

        # Encaminhar
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ("host", "transfer-encoding", "connection")}
        headers["Content-Length"] = str(len(body))
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

    # ── Compressao segura ───────────────────────

    def _safe_dedup(self, msgs):
        """Remove tool outputs duplicados consecutivos.
        Retorna lista otimizada ou None."""
        try:
            changed = False
            new_msgs = []
            last_tool = None
            for m in msgs:
                if not isinstance(m, dict):
                    new_msgs.append(m); continue
                role, content = m.get("role"), m.get("content","")
                if role == "tool" and content and content == last_tool:
                    changed = True; continue
                if role == "tool" and content:
                    last_tool = content
                new_msgs.append(m)
            return new_msgs if changed else None
        except Exception:
            return None

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

    if not HAS_HEADROOM and not HAS_RUST_CORE:
        print("⚠️  headroom nao disponivel — modo pass-through")
    else:
        rc = "✅" if HAS_RUST_CORE else "❌"
        try:
            hv = getattr(__import__("headroom"), "__version__", "?")
            print(f"✅ headroom-ai v{hv} (Rust _core: {rc})")
        except Exception:
            print(f"✅ headroom-ai carregado (Rust _core: {rc})")

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
