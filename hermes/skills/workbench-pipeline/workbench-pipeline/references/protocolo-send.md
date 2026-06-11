# PROTOCOLO SEND — Multi-IA Handoff

## Conceito
Cada shell pode ter MÚLTIPLAS IAs configuradas como "autoridades". O orquestrador consulta múltiplas IAs e combina resultados por consenso, paralelo ou sequencial.

## Modos de Operação

| Modo | Comportamento | Uso |
|------|--------------|-----|
| **consenso** | Todas as IAs votam, maioria vence | Decisões críticas (Shell 3) |
| **paralelo** | Todas executam simultaneamente, primeiro resultado vence | Latência mínima (Shell 1) |
| **sequencial** | Tenta IA 1, se falhar → IA 2, etc. | Confiabilidade (Shell 2) |
| **best-of-n** | Todas executam, melhor resultado (avaliado por DiffGate) vence | Qualidade máxima |
| **fallback** | Tenta IA principal, se timeout/erro → próxima | Resiliência |

## Configuração
```json
// runtime/protocol_send_config.json
{
  "shell3": {
    "autoridades": [...],
    "modo": "consenso",
    "timeout_s": 60
  },
  "shell2": {
    "autoridades": [...],
    "modo": "sequencial",
    "max_subtasks": 5
  },
  "shell1": {
    "autoridades": [...],
    "modo": "fallback",
    "temperature": 0.0
  }
}
```

## Implementação
- `src/workbench/shells/shell3_multi.py` — Decisor multi-adapter
- `src/workbench/shells/shell2_multi.py` — Planner multi-modelo
- `src/workbench/shells/protocol_send_config.py` — Config persistente
- `src/workbench/core/orchestrator_multi.py` — Orquestrador integrado
