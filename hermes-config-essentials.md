# Hermes 2.0 / NEO HERMES — Config Essentials
# Reaplicar apos update do Hermes Agent que resetar config.yaml
#
# Repo: https://github.com/guilhermecrepaldi/neo-hermes
# Descricao: NEO HERMES — Sistema autonomo de orquestracao multi-shell
#            com IA local + cloud, watchdog 24/7, pipeline de agentes,
#            telemetria obrigatoria, compressao de contexto (headroom.ai)

## Autoload (OBRIGATORIO — shellz-environment primeiro)
```
hermes config set agent.autoload_skills "shellz-environment,skill-router,ux-audit,stack-docs,auto-executor,auto-healing,output-coeso,roteador-economico,spec-agent,taste-skill,design-system-references"
```

## Compression (headroom.ai + compactor)
```
hermes config set compression.threshold 0.35
hermes config set compression.target_ratio 0.15
```

## Model (S3 = main brain, DeepSeek)
```
hermes config set model.default deepseek-v4-flash
hermes config set model.provider deepseek
```

## Browser (Chrome real com CDP)
```
hermes config set browser.cdp_url http://localhost:9222
```

## Chain Trust (NUNCA quebrar)
```
NUNCA remover shellz-environment do autoload
NUNCA usar DeepSeek para tarefas de S1 (Ollama)
NUNCA omitir telemetria ao final de resposta
NUNCA perder as melhorias — Fort Knox backup antes de update
SEMPRE backup: bash hermes-fort-knox.sh backup
```
