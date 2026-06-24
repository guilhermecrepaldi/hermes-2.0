"""Testes do Supabase Connector."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from supabase_connector import SupabaseClient, get_supabase, test_connection


def test_client_singleton():
    """SupabaseClient deve ser singleton por URL+key."""
    c1 = SupabaseClient("https://test.supabase.co", "key123")
    c2 = SupabaseClient("https://test.supabase.co", "key123")
    assert c1 is c2


def test_different_url_different_instance():
    """URLs diferentes devem ter instancias diferentes."""
    c1 = SupabaseClient("https://a.supabase.co", "key1")
    c2 = SupabaseClient("https://b.supabase.co", "key2")
    # Same url but different key -> different cache key
    assert c1 is not c2


def test_client_no_credentials():
    """Sem URL/KEY, connected deve ser False."""
    c = SupabaseClient("", "")
    assert not c.connected


def test_client_env_vars():
    """Deve ler de env vars se nao passar args."""
    old_url = os.environ.get("SUPABASE_URL", "")
    old_key = os.environ.get("SUPABASE_KEY", "")
    os.environ["SUPABASE_URL"] = "https://env.supabase.co"
    os.environ["SUPABASE_KEY"] = "env_key"
    c = SupabaseClient()
    assert c.url == "https://env.supabase.co"
    os.environ["SUPABASE_URL"] = old_url
    os.environ["SUPABASE_KEY"] = old_key


def test_get_supabase():
    """get_supabase deve retornar SupabaseClient."""
    db = get_supabase("https://test.supabase.co", "test")
    assert isinstance(db, SupabaseClient)


def test_test_connection_no_creds():
    """test_connection sem credenciais deve retornar dict com erro."""
    result = test_connection("", "")
    assert "connected" in result
    assert not result.get("connected", True)


def test_client_properties():
    """Propriedades basicas devem funcionar."""
    c = SupabaseClient("https://test.supabase.co", "test")
    assert hasattr(c, "connected")
    assert hasattr(c, "table")
    assert hasattr(c, "select")


def test_client_methods():
    """Metodos devem existir sem lancar excecao."""
    c = SupabaseClient("https://test.supabase.co", "test")
    # Sem credenciais, select deve retornar lista vazia
    result = c.select("test_table")
    assert isinstance(result, list)
    # Insert sem credenciais deve retornar None
    result = c.insert("test_table", {"name": "test"})
    assert result is None
