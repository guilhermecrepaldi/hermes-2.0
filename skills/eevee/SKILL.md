---
name: eevee
description: "EEVEE — test-time prompt learning for self-improving agents. Instead of manually tuning prompts, the model learns to adjust them during execution based on feedback. Ideal for multi-agent systems with complex orchestration."
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, prompt-optimization, self-improving-agents, multi-agent]
---

# EEVEE — Skill Auto-Gerado

## Fonte
Extraído da Edição #001 do TOP OF THE HOUR — IA
Card: "EEVEE: Aprendizado de Prompt em Tempo de Teste para Agentes Auto-Melhoráveis"

## O que é
EEVEE (arXiv:2606.XXXXX) é uma técnica que permite que o próprio modelo aprenda a ajustar seus prompts durante a execução com base no feedback recebido. Em vez de você passar horas ajustando prompts manualmente, o agente se auto-melhora durante o uso.

## Como implementar no Hermes 2.0
Se você mantém sistemas multiagentes complexos no Hermes, EEVEE pode reduzir a carga de manutenção de prompts:

1. **Wrapper de prompt adaptativo:** Crie um wrapper que coleta feedback (sucesso/falha) de cada execução de agente
2. **Loop de refinamento:** Implemente um loop onde o agente refina seu prompt após N falhas consecutivas
3. **Integração com memory:** Use a memória do Hermes para armazenar versões de prompts e seus resultados

## Comandos
```python
# Exemplo conceitual de wrapper EEVEE para Hermes
class EEVEEWrapper:
    def __init__(self, base_prompt):
        self.base_prompt = base_prompt
        self.history = []
    
    def execute_with_learning(self, task, max_refinements=3):
        prompt = self.base_prompt
        for attempt in range(max_refinements):
            result = agent_execute(task, prompt)
            if result.success:
                return result
            # Aprende com o feedback e ajusta o prompt
            prompt = self._refine_prompt(prompt, result.feedback)
        return result
```

## Referência
arXiv:2606.XXXXX — EEVEE paper
