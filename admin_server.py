#!/usr/bin/env python3
"""Hermes Admin Server — Entrypoint.
Start: python server.py
Access: http://localhost:8082/admin
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "watchdog"))

from admin_ui import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("HERMES_ADMIN_PORT", "8082"))
    host = os.environ.get("HERMES_ADMIN_HOST", "127.0.0.1")
    print(f"Hermes Admin UI: http://{host}:{port}/admin")
    uvicorn.run(app, host=host, port=port, log_level="info")
