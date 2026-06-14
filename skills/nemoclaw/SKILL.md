---
name: nemoclaw
description: "NVIDIA NemoClaw — platform for building secure autonomous coding agents with sandboxing, human approval policies, and complete audit logging. Combines CLAW microframework with NeMo guardrails for industrial use."
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, coding-agents, nvidia, sandboxing, enterprise]
---

# NemoClaw — Skill Auto-Gerado

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA
Card: "NVIDIA NemoClaw: Engenheiros de Software Autônomos e Seguros para Indústria com Agentes de IA"

## O que é
NemoClaw é uma plataforma da NVIDIA para construção de coding agents seguros para uso empresarial. Combina o microframework CLAW com guardrails da plataforma NeMo, oferecendo:
- **Sandboxing** — execução isolada de código gerado
- **Políticas de aprovação humana** para deploys
- **Logging completo** para auditoria

## Como implementar no Hermes 2.0
NemoClaw oferece um framework com guardrails embutidos que podem ser aplicados ao Hermes:

1. **Sandbox para código executado:** Use containers ou ambientes isolados para toda execução de código gerado por agentes
2. **Políticas de aprovação:** Implemente gate de confirmação humana para operações destrutivas (rm -rf, sudo, alteração de configs críticas)
3. **Audit trail:** Mantenha logging completo de todas as ações do agente (Hermes já faz isso via session_search)

## Comandos
```bash
# Integração conceitual com Hermes:
# Adicionar sandboxing ao terminal tool
hermes config set sandbox.enabled true
hermes config set sandbox.type docker  # ou container local
hermes config set approval.required_for "rm, sudo, chmod, deploy, write_config"
```

## Referência
https://developer.nvidia.com/nemo
https://github.com/NVIDIA/NeMo
