#!/usr/bin/env python3
"""Hermes Supabase Connector — CRUD + Realtime via supabase-py.
Uso:
  from supabase_connector import SupabaseClient
  db = SupabaseClient(url, key)
  await db.select("tabela").execute()
"""
from __future__ import annotations
import os
import json
from typing import Optional, Any, Dict, List
from dataclasses import dataclass

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

try:
    from logger_pro import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class SupabaseConfig:
    url: str = ""
    key: str = ""
    table: str = ""


class SupabaseClient:
    """Cliente Supabase com operacoes comuns.
    
    Singleton por URL+key.
    Metodos: select, insert, update, upsert, delete, rpc.
    """
    
    _instances: dict = {}
    
    def __new__(cls, url: str = "", key: str = ""):
        if not url:
            url = os.getenv("SUPABASE_URL", "")
        if not key:
            key = os.getenv("SUPABASE_KEY", "")
        
        cache_key = f"{url}:{key}"
        if cache_key not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[cache_key] = instance
        return cls._instances[cache_key]
    
    def __init__(self, url: str = "", key: str = ""):
        if self._initialized:
            return
        self._initialized = True
        
        self.url = url or os.getenv("SUPABASE_URL", "")
        self.key = key or os.getenv("SUPABASE_KEY", "")
        
        if not self.url or not self.key:
            logger.warning("Supabase: URL ou KEY nao configurados")
            self.client = None
            return
        
        if not HAS_SUPABASE:
            logger.error("supabase-py nao instalado: pip install supabase")
            self.client = None
            return
        
        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info("Supabase conectado")
        except Exception as e:
            logger.error(f"Falha ao conectar Supabase: {e}")
            self.client = None
    
    @property
    def connected(self) -> bool:
        return self.client is not None
    
    def table(self, name: str):
        """Acessa uma tabela."""
        if not self.client:
            raise RuntimeError("Supabase nao conectado")
        return self.client.table(name)
    
    def select(self, table: str, columns: str = "*",
               eq: Optional[dict] = None,
               limit: int = 100,
               order: Optional[str] = None) -> list:
        """SELECT com filtros opcionais."""
        if not self.client:
            return []
        try:
            query = self.client.table(table).select(columns)
            if eq:
                for k, v in eq.items():
                    query = query.eq(k, v)
            if order:
                query = query.order(order)
            result = query.limit(limit).execute()
            return result.data if hasattr(result, 'data') else []
        except Exception as e:
            logger.error(f"Supabase select: {e}")
            return []
    
    def insert(self, table: str, data: dict) -> Optional[dict]:
        """INSERT."""
        if not self.client:
            return None
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if hasattr(result, 'data') and result.data else None
        except Exception as e:
            logger.error(f"Supabase insert: {e}")
            return None
    
    def update(self, table: str, data: dict, eq: dict) -> Optional[dict]:
        """UPDATE com filtro."""
        if not self.client:
            return None
        try:
            query = self.client.table(table).update(data)
            for k, v in eq.items():
                query = query.eq(k, v)
            result = query.execute()
            return result.data[0] if hasattr(result, 'data') and result.data else None
        except Exception as e:
            logger.error(f"Supabase update: {e}")
            return None
    
    def delete(self, table: str, eq: dict) -> bool:
        """DELETE com filtro."""
        if not self.client:
            return False
        try:
            query = self.client.table(table).delete()
            for k, v in eq.items():
                query = query.eq(k, v)
            query.execute()
            return True
        except Exception as e:
            logger.error(f"Supabase delete: {e}")
            return False
    
    def rpc(self, fn: str, params: Optional[dict] = None) -> Any:
        """Chama funcao RPC (stored procedure)."""
        if not self.client:
            return None
        try:
            result = self.client.rpc(fn, params or {}).execute()
            return result.data if hasattr(result, 'data') else None
        except Exception as e:
            logger.error(f"Supabase rpc: {e}")
            return None
    
    def health(self) -> dict:
        """Verifica conectividade."""
        if not self.client:
            return {"connected": False, "error": "nao configurado"}
        try:
            # Tenta listar tabelas via schema
            r = self.client.table("_dummy").select("count", count="exact").limit(1).execute()
            return {"connected": True, "status": "ok"}
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    def list_tables(self) -> list:
        """Lista tabelas via RPC ou information_schema."""
        try:
            result = self.rpc("list_tables")
            if result:
                return result
            # Fallback: tenta query direta
            from supabase import create_client
            r = self.client.table("information_schema.tables")                 .select("table_name")                 .eq("table_schema", "public")                 .execute()
            return [t["table_name"] for t in (r.data or [])]
        except Exception:
            return []


# ═══════════════════════════════════════════════════
# FUNCOES DE CONVENIENCIA
# ═══════════════════════════════════════════════════

def get_supabase(url: str = "", key: str = "") -> SupabaseClient:
    """Obtem instancia do SupabaseClient (singleton)."""
    return SupabaseClient(url, key)


def test_connection(url: str = "", key: str = "") -> dict:
    """Testa conexao com Supabase."""
    db = SupabaseClient(url, key)
    return db.health()
