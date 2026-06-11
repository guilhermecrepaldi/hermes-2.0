---
name: shellz
description: "Shellz — arquitetura de colaboracao entre LLMs com 3 shells + roteador automatico + fallback chain + relatorio de economia"
category: hermes-2.0
tags: [shellz, routing, multi-llm, orchestration, economy, hermes-2.0]
---

# 🐚 Shellz — Arquitetura de Colaboração entre LLMs

## O que é
Shellz é a arquitetura de **colaboração inteligente entre LLMs** do Hermes 2.0.
Cada requisição é classificada e roteada para o shell mais adequado,
maximizando economia sem sacrificar qualidade.

## Os 3 Shells

```
Shell 1 — LOCAL (grátis)           Shell 2 — MÉDIO ($$)          Shell 3 — PESADO ($$$)
┌──────────────────────┐          ┌──────────────────────┐       ┌──────────────────────┐
│  Ollama              │          │  DeepSeek v4         │       │  Claude / GPT        │
│  qwen2.5-coder:7b    │          │  deepseek-chat       │       │  claude-sonnet /     │
│                      │          │                      │       │  gpt-4o              │
│  Custo: R$ 0         │          │  Custo: ~R$0.003/req │       │  Custo: ~R$0.03/req  │
│  Latência: ~2s       │          │  Latência: ~5s       │       │  Latência: ~8s       │
│  Offline: ✅         │          │  Offline: ❌         │       │  Offline: ❌         │
│  Privacidade: total  │          │  Privacidade: API    │       │  Privacidade: API    │
└──────────────────────┘          └──────────────────────┘       └──────────────────────┘
```

## Classificador Automático

Antes de executar qualquer ação, eu (o agente) DEVO classificar:

### 🟢 SIMPLES → Shell 1 (Ollama local)
**Quando usar:** Tarefas que não exigem raciocínio profundo
- `ls`, `grep`, `cat` de arquivos
- Comandos shell simples (cp, mv, rm)
- Leitura de arquivos pequenos (< 50 linhas)
- Operações git básicas (add, commit, status)
- Navegação de diretórios
- Qualquer comando que seja 1-2 chamadas de terminal

**MO:** Executo o comando diretamente, sem necessidade de LLM. Se precisar de LLM, uso Ollama.

### 🟡 MÉDIO → Shell 2 (DeepSeek v4)
**Quando usar:** Tarefas que exigem raciocínio médio
- Debug de código (erros, exceções)
- Explicar conceitos técnicos
- Escrever funções/módulos pequenos
- Revisar PRs / code review
- Análise de logs
- Transformação de dados
- Qualquer coisa que precise de >3 tool calls

**MO:** Uso o DeepSeek como provedor principal (padrão).

### 🔴 COMPLEXO → Shell 3 (Claude/GPT)
**Quando usar:** Apenas quando necessário
- Estratégia de arquitetura
- Decisões de design de sistema
- Criação de skills complexos
- Análise profunda de trade-offs
- Quando Shell 2 falhou e precisa de fallback

**MO:** Mudar provider manualmente para Claude/GPT.

## Fallback Chain

Se um shell falhar, subir automaticamente:

```
Shell 1 (Ollama) caiu?   → Shell 2 (DeepSeek)     → continua
Shell 2 (DeepSeek) caiu? → Shell 3 (Claude/GPT)    → continua
Shell 3 (Claude/GPT) caiu? → relatar erro ao usuário
```

## Relatório de Economia

Ao final de CADA resposta, DEVO incluir o gasto estimado:

```
═══════════════════════════════════
🐚 SHELLZ — Relatório de Economia
═══════════════════════════════════
Shell 1 (Ollama local):   3 chamadas · R$ 0,00
Shell 2 (DeepSeek):       2 chamadas · R$ 0,006
Shell 3 (Claude/GPT):     0 chamadas · R$ 0,00
───────────────────────────────────
Total:                    5 chamadas · R$ 0,006
Economia vs Claude:       93% (R$ 0,08 economizados)
═══════════════════════════════════
```

## Verificação de Saúde

No início de cada sessão:
1. Verificar se Ollama está rodando: `curl -s http://localhost:11434/api/version`
2. Se não estiver: tentar iniciar com `wscript.exe /B D:\projetos\hermes-watchdog\ollama_invisible.vbs`
3. Se não conseguir: Shell 1 fica indisponível, usar fallback

## Estados do Sistema

ShelIz mantém 3 contadores por sessão:
| Shell | Chamadas | Custo | Status |
|-------|----------|-------|--------|
| 🟢 Shell 1 | `_shellz_s1` | R$ 0 | online/offline |
| 🟡 Shell 2 | `_shellz_s2` | ~R$0.003/call | online |
| 🔴 Shell 3 | `_shellz_s3` | ~R$0.03/call | configurado |

## Modelos Carregados no Ollama
```
qwen2.5-coder:7b     → Shell 1 (coding tasks)
qwen2.5:7b           → Shell 1 (general)
qwen2.5:14b          → Shell 1 (heavy, quando qwen7b não basta)
llama3.1:8b          → Shell 1 (alternativa)
mistral:latest       → Shell 1 (leve)
deepseek-coder:6.7b  → Shell 1 (coding alternativo)
nomic-embed-text     → embeddings
```

## Auto-Start
- Ollama inicia automaticamente via atalho na pasta Startup
- VBS launcher invisível: `D:\\projetos\\hermes-watchdog\\ollama_invisible.vbs`
- Watchdog guardian monitora e reinicia se cair
- Shellz Tray Icon inicia junto (atalho Startup: `ShellzTray.lnk`)

## Shellz Tray Icon (ícone na bandeja do Windows)

O ícone na bandeja do sistema (ao lado do relógio) permite controlar o Ollama sem abrir janelas.

### Estado visual do ícone
| Cor | Estado | Significado |
|-----|--------|-------------|
| 🟢 **Verde** | Rodando | Ollama ativo, Shell 1 disponível |
| 🟠 **Laranja** | Pausado | GPU livre para jogos |
| ⚫ **Cinza** | Parado | Ollama não está rodando |

### Interações
| Ação | Resultado |
|------|-----------|
| 🖱️ **Clique esquerdo** | Toggle Pausar/Retomar (alterna entre 🟢 e 🟠) |
| 🖱️ **Clique direito** | Menu: Pausar, Retomar, Ver Status, Sair |
| 🔔 **Balloon notification** | Notificação ao pausar/retomar |

### Arquivos
| Arquivo | Função |
|---------|--------|
| `D:\\projetos\\hermes-watchdog\\shellz_tray.ps1` | Script PowerShell do tray icon |
| `D:\\projetos\\hermes-watchdog\\shellz_tray.vbs` | Launcher VBS (invisível) para o PowerShell |
| `D:\\projetos\\hermes-watchdog\\create_tray_shortcuts.ps1` | Cria atalhos Startup + Desktop |
| `%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\ShellzTray.lnk` | Auto-start no login |

### Recriação de atalhos
Se os atalhos forem deletados, execute:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\\projetos\\hermes-watchdog\\create_tray_shortcuts.ps1"
```

## Controles do Usuário — Pausar/Retomar

O usuário pode pausar o Ollama a qualquer momento para liberar GPU para jogos ou outras tarefas.

### 🎮 Pausar (liberar GPU)
```
Duas formas:
1. Atalho na Desktop: "🐚 Shellz Pausar"
2. Comando: D:\projetos\hermes-watchdog\shellz_pausar.bat
```
O que faz:
- Para o processo ollama.exe
- Libera memória GPU via nvidia-smi --gpu-reset
- Cria arquivo `.shellz_paused` (watchdog não reinicia)

### ▶️ Retomar (reativar Shell 1)
```
Duas formas:
1. Atalho na Desktop: "🐚 Shellz Retomar"  
2. Comando: D:\projetos\hermes-watchdog\shellz_retomar.bat
```
O que faz:
- Inicia Ollama via VBS (invisível)
- Aguarda até ficar pronto (verifica /api/version)
- Remove arquivo `.shellz_paused`

### Integração com Watchdog
- Se `.shellz_paused` existir → guardian NÃO reinicia o Ollama
- Se `.shellz_paused` NÃO existir e Ollama cair → guardian reinicia normalmente
