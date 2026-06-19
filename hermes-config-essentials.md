# Hermes 2.0 — Config Essentials
# Reaplicar apos update do Hermes Agent que resetar config.yaml
# Uso: hermes config set agent.autoload_skills "..."
#      (copiar linhas compression abaixo para config.yaml manualmente)

# === AUTOLOAD SKILLS ===
# Carregadas automaticamente em toda sessao:
hermes config set agent.autoload_skills "neo-hermes,auto-executor,auto-healing,output-coeso,roteador-economico,spec-agent,taste-skill,hermes-hooks"

# === COMPRESSAO DE CONTEXTO ===
# Abaixo de agent: no config.yaml, adicionar:
compression:
  enabled: true
  threshold: 0.35
  target_ratio: 0.15
  protect_first_n: 3
  protect_last_n: 20
