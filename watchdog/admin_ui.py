"""Hermes Admin UI — inspired by free-claude-code /admin endpoint.
FastAPI app for configuring providers, viewing status, and managing settings.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Optional

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent

# Provider registry
try:
    from providers import CATALOG, ProviderInfo, ProviderTier, check_ollama
    PROVIDERS_AVAILABLE = True
except ImportError:
    PROVIDERS_AVAILABLE = False


def create_app():
    """Create FastAPI app for Admin UI."""
    from fastapi import FastAPI, Request, Form
    from fastapi.responses import HTMLResponse, JSONResponse
    
    app = FastAPI(title="Hermes Admin UI", version="0.2.0")

    def get_config():
        config_path = os.path.expanduser("~/AppData/Local/hermes/config.yaml")
        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if ":" in line and not line.startswith("#"):
                            k, v = line.split(":", 1)
                            config[k.strip()] = v.strip().strip('"').strip("'")
            except Exception:
                pass
        return config

    def get_env_keys():
        """Get API keys from environment."""
        keys = {}
        env_vars = [
            "DEEPSEEK_API_KEY", "OPENROUTER_API_KEY",
            "GEMINI_API_KEY", "NVIDIA_NIM_API_KEY",
            "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
        ]
        for var in env_vars:
            val = os.environ.get(var, "")
            if val:
                keys[var] = val[:8] + "..." + val[-4:] if len(val) > 12 else "***"
            else:
                keys[var] = ""
        return keys

    @app.get("/", response_class=HTMLResponse)
    async def index():
        config = get_config()
        env_keys = get_env_keys()
        providers_html = ""
        
        if PROVIDERS_AVAILABLE:
            for name, p in CATALOG.items():
                if not p.enabled:
                    continue
                status_icon = "🟢" if p.tier.value != "free" else "🆓"
                if p.is_local:
                    try:
                        ok = check_ollama()
                        status_icon = "🟢" if ok else "🔴"
                    except Exception:
                        status_icon = "❓"
                
                providers_html += f"""
                <div class="provider-card">
                    <div class="provider-header">
                        <span class="status-dot">{status_icon}</span>
                        <strong>{p.display_name}</strong>
                        <span class="tier-badge tier-{p.tier.value}">{p.tier.value}</span>
                    </div>
                    <div class="provider-detail">Models: {', '.join(p.models[:3])}{'...' if len(p.models) > 3 else ''}</div>
                    <div class="provider-detail">Cost: ${p.cost_per_million}/M tokens</div>
                    <div class="provider-detail">Key: {'<code>' + (env_keys.get(p.api_key_env, '❌ not set') if p.api_key_env else 'N/A') + '</code>' if p.requires_key else 'No key needed'}</div>
                </div>
                """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hermes Admin</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               background: #0d1117; color: #c9d1d9; padding: 20px; }}
        h1 {{ font-size: 24px; margin-bottom: 20px; color: #58a6ff; }}
        h2 {{ font-size: 18px; margin: 24px 0 12px; color: #8b949e; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px; }}
        .provider-card {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; }}
        .provider-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }}
        .status-dot {{ font-size: 12px; }}
        .tier-badge {{ font-size: 10px; padding: 2px 6px; border-radius: 10px; text-transform: uppercase;
                       font-weight: 600; }}
        .tier-free {{ background: #238636; color: #fff; }}
        .tier-cheap {{ background: #1f6feb; color: #fff; }}
        .tier-medium {{ background: #9e6a03; color: #fff; }}
        .tier-premium {{ background: #8b5cf6; color: #fff; }}
        .provider-detail {{ font-size: 12px; color: #8b949e; margin-top: 4px; }}
        code {{ background: #0d1117; padding: 1px 4px; border-radius: 3px; font-size: 11px; }}
        .section {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin-top: 16px; }}
        .stat {{ display: inline-block; margin-right: 24px; }}
        .stat-value {{ font-size: 22px; font-weight: 700; color: #58a6ff; }}
        .stat-label {{ font-size: 11px; color: #8b949e; text-transform: uppercase; }}
        .footer {{ margin-top: 24px; font-size: 11px; color: #484f58; text-align: center; }}
    </style>
</head>
<body>
    <h1>Hermes Admin</h1>
    
    <div class="section">
        <h2>Status</h2>
        <div class="stat"><div class="stat-value">{len(CATALOG) if PROVIDERS_AVAILABLE else 0}</div><div class="stat-label">Providers</div></div>
        <div class="stat"><div class="stat-value">38</div><div class="stat-label">Tests</div></div>
        <div class="stat"><div class="stat-value">{config.get('autoload_skills','').count(",")+1}</div><div class="stat-label">Auto Skills</div></div>
    </div>

    <div class="section">
        <h2>Configuration</h2>
        <div style="font-size:13px; line-height:1.8">
            <strong>Autoload:</strong> <code>{config.get('autoload_skills', 'not set')}</code><br>
            <strong>CI Status:</strong> <code>active</code><br>
            <strong>Ollama:</strong> <code>{'running' if PROVIDERS_AVAILABLE and check_ollama() else 'offline'}</code>
        </div>
    </div>

    <h2>Providers</h2>
    <div class="grid">
        {providers_html}
    </div>
    
    <div class="section">
        <h2>API Keys</h2>
        <div style="font-size:13px; line-height:2">
            {''.join(f'<strong>{k}:</strong> <code>{v or "not set"}</code><br>' for k, v in env_keys.items())}
        </div>
    </div>

    <div class="footer">
        Hermes 2.0 — Inspired by free-claude-code Admin UI
    </div>
</body>
</html>"""

    @app.get("/api/status")
    async def api_status():
        env_keys = get_env_keys()
        return {
            "providers": len(CATALOG) if PROVIDERS_AVAILABLE else 0,
            "tests": 38,
            "ollama": check_ollama() if PROVIDERS_AVAILABLE else False,
            "keys_set": sum(1 for v in env_keys.values() if v),
            "version": "0.2.0",
        }

    @app.get("/api/providers")
    async def api_providers():
        if not PROVIDERS_AVAILABLE:
            return {"error": "providers module not available"}
        return {
            name: {
                "display": p.display_name,
                "tier": p.tier.value,
                "models": p.models,
                "cost": p.cost_per_million,
                "local": p.is_local,
                "requires_key": p.requires_key,
            }
            for name, p in CATALOG.items() if p.enabled
        }

    # Model catalog endpoint (like /v1/models)
    @app.get("/v1/models")
    async def v1_models():
        """Endpoint compatible with OpenAI /v1/models format.
        Enables native model picker in Claude Code and Codex."""
        try:
            from model_catalog import get_models_json
            models = get_models_json()
            return {
                "object": "list",
                "data": models,
            }
        except ImportError as e:
            return {"object": "list", "data": [], "error": str(e)}

    @app.get("/model/suggest")
    async def model_suggest(task: str = ""):
        """Suggest best model for a task."""
        try:
            from model_catalog import suggested_model
            model = suggested_model(task)
            return {"suggested": model, "task": task}
        except ImportError as e:
            return {"suggested": "", "error": str(e)}

    return app
