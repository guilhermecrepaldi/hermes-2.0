#!/usr/bin/env python3
"""
Hermes QuickStart - Monitor de Quota e Auto-Switch
Sincroniza o status da quota e decide o melhor LLM para a próxima tarefa.
"""
import subprocess
import json
import os
import time
import sys

# Caminhos absolutos para evitar erros de diretório
BASE_DIR = r"D:\projetos\hermes-watchdog"
WORKBENCH = os.path.join(BASE_DIR, "hermes_workbench.py")
QUOTA_FILE = os.path.join(BASE_DIR, "quota_config.json")

def run_command(args):
    cmd = [sys.executable, WORKBENCH] + args
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return result.stdout

def main():
    print("🚀 Iniciando Monitor de Quota HERMES 3.1...")
    
    # 1. Verifica Quota Atual
    print("\n[PASSO 1] Verificando quota disponível...")
    quota_output = run_command(["quota-check"])
    print(quota_output)
    
    # Lê valor do arquivo para lógica
    try:
        with open(QUOTA_FILE, 'r') as f:
            quota_data = json.load(f)
            remaining = quota_data.get("quota_remaining", 0)
    except Exception as e:
        print(f"❌ Erro ao ler quota: {e}")
        remaining = 1000 # Fallback seguro
    
    # 2. Testa Roteamento para diferentes cenários
    print("\n[PASSO 2] Testando Roteador Inteligente (Simulando tarefas)...")
    
    scenarios = [
        {"name": "Tarefa Ultra-Complexa", "complexity": 9},
        {"name": "Tarefa de Codificação Padrão", "complexity": 5},
        {"name": "Tarefa Simples/Repetitiva", "complexity": 2}
    ]
    
    for sc in scenarios:
        print(f"\n--- Cenário: {sc['name']} ---")
        router_output = run_command(["intelligence-router", str(sc['complexity']), str(remaining)])
        print(router_output)
        time.sleep(0.5)

    print("\n✅ Sistema operacional. Pronto para receber tarefas.")

if __name__ == "__main__":
    main()
