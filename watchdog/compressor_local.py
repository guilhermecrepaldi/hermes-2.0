#!/usr/bin/env python3
"""Compressor Local — Usa Ollama (S1) para comprimir contexto antes do S3.
Gratis ($0), rapido (ms), ja instalado.
Alternativa ao headroom.ai enquanto Rust core nao compila no Windows.
"""
import json
import hashlib
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    from logger_pro import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

CACHE_DIR = Path.home() / ".hermes" / "compressor_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Limite: so comprime se tiver mais que N tokens
COMPRESS_THRESHOLD = 500


def estimar_tokens(texto: str) -> int:
    """Estimativa rapida de tokens (4 chars ~ 1 token)."""
    return len(texto) // 4


def comprimir_contexto(texto: str, modelo: str = "qwen2.5-coder:7b") -> dict:
    """Comprime texto usando Ollama local (S1, gratis).
    
    Args:
        texto: Texto a ser comprimido
        modelo: Modelo Ollama para compressao
    
    Returns:
        Dict com texto comprimido e metricas
    """
    tokens_antes = estimar_tokens(texto)
    
    if tokens_antes < COMPRESS_THRESHOLD:
        return {
            "texto": texto,
            "tokens_antes": tokens_antes,
            "tokens_depois": tokens_antes,
            "economia": 0,
            "motivo": "abaixo do limiar",
        }
    
    # Cache por hash do conteudo
    hash_key = hashlib.md5(texto.encode()[:1000]).hexdigest()
    cache_file = CACHE_DIR / f"{hash_key}.json"
    
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except:
            pass
    
    try:
        import requests
        
        prompt = f"""Comprima o texto abaixo mantendo APENAS as informacoes essenciais.
Remova repeticoes, boilerplate, e detalhes irrelevantes.
Mantenha dados numericos, nomes, comandos e conclusoes.

TEXTO:
{texto[:8000]}

RESUMO COMPRIMIDO:"""
        
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": modelo,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 2048, "temperature": 0.1},
            },
            timeout=30,
        )
        
        if resp.status_code == 200:
            comprimido = resp.json().get("response", texto)
        else:
            comprimido = texto
    except Exception as e:
        logger.warning(f"Compressor local falhou: {e}")
        comprimido = texto
    
    tokens_depois = estimar_tokens(comprimido)
    economia = max(0, tokens_antes - tokens_depois)
    
    resultado = {
        "texto": comprimido,
        "tokens_antes": tokens_antes,
        "tokens_depois": tokens_depois,
        "economia": economia,
        "economia_pct": round(economia / max(tokens_antes, 1) * 100, 1),
        "modelo": modelo,
    }
    
    # Salvar cache
    try:
        cache_file.write_text(json.dumps(resultado))
    except:
        pass
    
    return resultado


def comprimir_mensagens(mensagens: List[dict], modelo: str = "qwen2.5-coder:7b") -> List[dict]:
    """Comprime o conteudo das mensagens (exceto system)."""
    comprimidas = []
    for msg in mensagens:
        if msg.get("role") == "system" or msg.get("role") == "assistant":
            comprimidas.append(msg)
            continue
        
        if msg.get("role") == "user":
            conteudo = msg.get("content", "")
            if estimar_tokens(conteudo) >= COMPRESS_THRESHOLD:
                resultado = comprimir_contexto(conteudo, modelo)
                comprimidas.append({
                    "role": "user",
                    "content": resultado["texto"],
                    "_compressao": {
                        "tokens_antes": resultado["tokens_antes"],
                        "tokens_depois": resultado["tokens_depois"],
                        "economia_pct": resultado["economia_pct"],
                    }
                })
                continue
        
        comprimidas.append(msg)
    
    return comprimidas


def stats_cache() -> dict:
    """Estatisticas do cache de compressao."""
    if not CACHE_DIR.exists():
        return {"cache_hits": 0, "cache_misses": 0}
    
    hits = len(list(CACHE_DIR.glob("*.json")))
    return {"cache_hits": hits, "cache_dir": str(CACHE_DIR)}
