---
name: oss-absorb
description: "Pipeline para baixar, analisar e integrar software open-source de terceiros ao proprio Hermes — com gate de licenca obrigatorio, estrategia de integracao decidida por S3, e ledger de atribuicao. Tambem serve como base para o Hermes propor e construir sua propria proxima versao (self-fork)."
category: autonomous-ai-agents
tags: [oss, license-compliance, integration, self-improvement, code-reuse, supply-chain, fork]
---

# OSS Absorb — Hermes assimila software de terceiros

## Pipeline (A0 → A6)

```
A0 INTAKE → Normaliza pedido (URL direta OU busca por capacidade)
A1 DISCOVERY → Busca e ranqueia candidatos (se nao tem URL)
A2 CLONE+TRIAGE → Clona raso, roda project_load() (s3_headroom.py)
A3 LICENSE GATE → 🛑 Bloqueia ou libera. NAO-NEGOCIAVEL.
A4 DECISION_PACKAGE (S3) → Escolhe: wrap | port | vendor | skill-only
A5 ARCHITECTURE (S2) → Decide onde entra no Hermes
A6 EXECUCAO + QUALITY GATE + ATTRIBUTION LEDGER + COMMIT
```

## Regras de Ouro (nao-negociaveis)

1. **Sem licenca = sem absorcao.** Ponto final.
2. **GPL/AGPL nunca entra no mesmo processo do Hermes.** So subprocess externo.
3. **Toda absorcao gera linha em THIRD_PARTY_NOTICES.md.** Sem excecao.
4. **Nunca execute codigo de terceiros antes do gate A3.** So leitura (clone, grep).
5. **Toda integracao nova segue checklist A6.** Nao pular.
6. **Confirmacao humana antes de clonar**, exceto se ja autorizado.
7. **Nunca vendorizar/portar de repo sem URL publica verificavel.**

## Estrategias de Integracao (A4)

| Estrategia | O que significa | Quando usar |
|---|---|---|
| **wrap** | Subprocess externo, sem copiar codigo | Licenca restritiva, projeto grande, linguagem incompativel |
| **port** | Reescrever logica em Python stdlib (sem copiar) | Licenca permissiva + parte util pequena |
| **vendor** | Dependencia pip (requirements.txt) | Licenca permissiva/LGPL + lib madura |
| **skill-only** | So documentar em SKILL.md | CLI externa ja cobre o caso |

## Quality Gate (A6) — checklist pre-commit
- [ ] Nenhum path absoluto hardcoded
- [ ] Nenhum subprocess.run sem check returncode
- [ ] Nenhum except silencioso
- [ ] Dependencias pip em requirements.txt
- [ ] Teste novo em master_test.py
- [ ] Atribuicao em THIRD_PARTY_NOTICES.md
- [ ] Se wrap: verifica binario no PATH antes de chamar

## Comandos (hermes-workbench)

```
absorb <url>                    Pipeline completo A0→A6
absorb <url> --dry-run          Roda ate A4 e mostra, sem integrar
absorb --find "<capacidade>"    Roda A1 (discovery) lista 3 melhores
absorb list                     Le THIRD_PARTY_NOTICES.md
absorb check <url>              So A2+A3 (clone + veredito licenca)
```
