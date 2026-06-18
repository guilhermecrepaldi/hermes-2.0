---
name: auto-executor
description: "Loop Plan→Execute→Verify para tarefas complexas. Planeja, executa, verifica e corrige automaticamente com até 3 tentativas. Substitui execução linear por ciclo validativo com evidências."
category: software-development
tags: [workflow, loop, plan-execute-verify, auto-correcao, arquitetura]
---

# Auto-Executor — Loop Plan → Execute → Verify

## Trigger
Carregue esta skill quando o usuário pedir para **construir, implementar, refatorar, criar, configurar ou executar** algo que exija múltiplos passos (3+ ferramentas).

## Workflow

### Fase 1: PLAN
1. Receba a tarefa do usuário
2. Crie um plano detalhado com passos numerados e ordem
3. Valide o plano antes de executar:
   - Cada passo é executável com as ferramentas disponíveis?
   - Dependências existem? (arquivos, diretórios, pacotes)
   - Riscos identificados? (sobrescrever arquivos, instalar pacotes)
4. Apresente o plano ao usuário via `clarify` com 2 opções:
   - "✅ Aprovado, executar"
   - "✏️ Ajustar plano" (usuário descreve mudanças)
5. Se rejeitado: ajuste e replaneje (máx 2 iterações)

### Fase 2: EXECUTE
6. Execute cada passo do plano sequencialmente
7. Após CADA passo, verifique o resultado:
   - `exit_code == 0`? ✅ Avance
   - `exit_code != 0` ou output vazio? ⚠️ Entre no loop de correção

### Fase 3: VERIFY
8. Após TODOS os passos, valide o entregável final:
   - Arquivo esperado existe? (`ls -la`)
   - Teste passa? (`pytest`, `npm test`)
   - Serviço responde? (`curl http://localhost:PORTA`)
9. Se validação falhou (máx 3 tentativas no total):
   - Analise o erro real (leia o output, não invente)
   - Ajuste o passo que falhou
   - Reexecute só os passos necessários
10. Se sucesso:
    - Reporte o resultado com evidências (exit codes, paths, URLs)
    - Use `delivery-report` se disponível

## Loop de Correção Interno

```
para cada passo no plano:
    para tentativa in 1..3:
        resultado = executar(passo)
        se resultado.ok:
            break  # próximo passo
        senão:
            log(f"Passo {passo} falhou: {resultado.erro}")
            analisar_causa_raiz()
            se tentativa == 1: ajustar_estrategia()
            se tentativa == 2: tentar_abordagem_diferente()
            se tentativa == 3: reportar_erro_e_parar()
```

## Evidências Obrigatórias no Report

| O quê | Como |
|-------|------|
| Arquivos criados | `ls -la path/`, `wc -l arquivo` |
| Testes passando | `pytest -q`, `node -e "require('...')"` |
| Serviço rodando | `curl -s -o /dev/null -w "%{http_code}" http://localhost:PORTA` |
| Dependências | `pip list \| grep pacote`, `npm ls pacote` |
| Git status | `git log --oneline -3`, `git status --short` |

## Anti-Padrões
- ❌ Executar sem plano para tarefas com 3+ passos
- ❌ Ignorar erro e continuar
- ❌ Reportar sucesso sem evidência
- ❌ "Tente isso" sem testar
