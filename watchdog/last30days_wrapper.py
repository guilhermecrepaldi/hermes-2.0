#!/usr/bin/env python3
"""Hermes wrapper para last30days — pesquisa em tempo real.
Instalado em: ~/last30days-skill/
Repo: https://github.com/mvanhorn/last30days-skill
"""
import sys
import os
from pathlib import Path

LAST30DAYS_DIR = Path.home() / "last30days-skill"
SKILL_DIR = LAST30DAYS_DIR / "skills" / "last30days"

def pesquisar(topicos: str) -> str:
    """Pesquisa topicos nos ultimos 30 dias via last30days.
    
    Args:
        topicos: Topico(s) para pesquisar (ex: 'DeepSeek R2 launch')
    
    Returns:
        Sumario sintetizado com citacoes
    """
    os.chdir(str(LAST30DAYS_DIR))
    
    # Executa o script de pesquisa
    script = SKILL_DIR / "scripts" / "research.js"
    if script.exists():
        os.system(f'node "{script}" "{topicos}"')
    else:
        # Fallback: le o SKILL.md para instrucoes
        skill_file = SKILL_DIR / "SKILL.md"
        if skill_file.exists():
            with open(skill_file) as f:
                content = f.read()
            print(f"SKILL.md carregado ({len(content)} chars)")
            print(f"Use: last30days '{topicos}' no terminal")
        else:
            print(f"last30days nao encontrado em {SKILL_DIR}")

if __name__ == "__main__":
    topicos = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hermes Agent"
    pesquisar(topicos)
