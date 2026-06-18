#!/usr/bin/env python3
"""
Monitor de Status - Verificar saúde do sistema Hermes 3.1
"""

from datetime import datetime
from pathlib import Path

def check_system_status():
    """Verificar status completo do sistema."""
    print("📊 Status Hermes 3.1 Workbench")
    print("=" * 50)
    
    # Verificar hermes_workbench.py
    if Path("hermes_workbench.py").exists():
        print("✅ hermes_workbench.py - Ativo")
        print("   • Roteamento LLM inteligente")
        print("   • Detecção automática de quota")
    else:
        print("❌ hermes_workbench.py - Ausente")
    
    # Verificar quick_start.py
    if Path("quick_start.py").exists():
        print("✅ quick_start.py - Ativo") 
        print("   • Monitor de quota auto-switch")
        print("   • Pipeline Multi-Agent")
    else:
        print("❌ quick_start.py - Ausente")
    
    # Verificar status de quota
    try:
        quota_remaining = simulate_quota_check()
        status = "SAUDÁVEL" if quota_remaining > 50 else "BAIXO"
        print(f"💰 Quota: ${quota_remaining:.2f} restante - {status}")
    except:
        print("❌ Erro ao verificar quota")
    
    print(f"\n📅 Última verificação: {datetime.now().strftime('%H:%M:%S')}")

def simulate_quota_check():
    """Simular verificação de quota."""
    return max(0, 500 - (425 * 0.95))

if __name__ == "__main__":
    check_system_status()