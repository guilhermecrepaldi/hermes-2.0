# Hermes 2.0 — Config Essentials
# Reaplicar apos update do Hermes Agent que resetar config.yaml
# Uso: hermes config set agent.autoload_skills "..."
#      hermes config set compression.threshold 0.35
#      hermes config set compression.target_ratio 0.15

## AUTOLOAD SKILLS (skill-router DEVE ser o primeiro)
autoload_skills: skill-router,stack-docs,auto-executor,auto-healing,output-coeso,roteador-economico,spec-agent,taste-skill,design-system-references

## COMPRESSION
agent:
  compression:
    threshold: 0.35
    target_ratio: 0.15
