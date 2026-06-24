# Hermes 2.0 — Config Essentials
# Reaplicar apos update do Hermes Agent que resetar config.yaml
# Uso: hermes config set agent.autoload_skills "..."
#      hermes config set compression.threshold 0.35

## Autoload (OBRIGATORIO — primeira skill SEMPRE shellz-environment)
```
hermes config set agent.autoload_skills "shellz-environment,skill-router,ux-audit,stack-docs,auto-executor,auto-healing,output-coeso,roteador-economico,spec-agent,taste-skill,design-system-references"
```

## Compression
```
hermes config set compression.threshold 0.35
hermes config set compression.target_ratio 0.15
```

## Model (S3 = main brain, $0.30/M)
```
hermes config set model.default deepseek-v4-flash
hermes config set model.provider deepseek
```

## Browser (Chrome real com CDP)
```
hermes config set browser.cdp_url http://localhost:9222
```

## Chain Trust
```
NUNCA remover shellz-environment do autoload
NUNCA usar DeepSeek para tarefas de S1 (Ollama)
NUNCA omitir telemetria ao final de resposta
```
