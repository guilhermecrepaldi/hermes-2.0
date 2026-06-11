---
name: workbench-pipeline
description: "Orquestração multi-shell industrial com handoff entre IAs, execução local (Ollama) e validação DiffGate. Baseado no Workbench AI.Manager."
category: autonomous-ai-agents
tags: [multi-agent, orchestration, handoff, ollama, diffgate, mcp, pipeline, autonomous]
---

# Workbench Pipeline — Hermes 2.0 Multi-Shell Orchestrator

## Hermes 2.0 — Identity
Este skill é o coração do **Hermes 2.0**, a evolução integrada do sistema. Não é um add-on — é como o Hermes opera nativamente.

**Princípios Hermes 2.0:**
1. **Tudo é Hermes** — skills, cron, watchdog, workbench são componentes do mesmo sistema
2. **Multi-shell por padrão** — toda tarefa avalia qual shell usar, não joga tudo no modelo mais caro
3. **Auto-recuperação** — watchdog monitora 24/7, se travar >25min, mata e recovery automático
4. **Um programa só** — ligou o Hermes, tudo funciona. Cron inicia watchdog em 60s.

## Arquitetura

```
USUÁRIO/REQUEST
    │
    ▼
┌─────────────────────────────────────────────────┐
│            🧠 SHELL 3 — DECISÃO                 │
│   ClaudeAdapter · GeminiAdapter · OpenAIAdapter │
│   GrokAdapter · (multi: paralelo/sequencial)    │
│   NUNCA retorna código — só decisão + plano     │
└─────────────────────┬───────────────────────────┘
                      │ DECISION_PACKAGE
                      ▼
┌─────────────────────────────────────────────────┐
│          🗂️ SHELL 2 — PLANEJAMENTO              │
│   Decompõe em subtarefas · BudgetEstimator      │
│   TokenCompressor · SemanticCache               │
│   VALIDA: DiffGate (AST, imports, injeção)      │
└─────────────────────┬───────────────────────────┘
                      │ Subtasks + Plan
                      ▼
┌─────────────────────────────────────────────────┐
│     ⚙️ SHELL 1 — EXECUÇÃO LOCAL (Ollama)       │
│   Gera código · Nunca decide · Nunca escala     │
│   Params: model, temperature, num_ctx, timeout  │
└─────────────────────┬───────────────────────────┘
                      │ Code patch
                      ▼
┌─────────────────────────────────────────────────┐
│        📁 MCP — FILESYSTEM PATCHING             │
│   Aplica patches aprovados pelo DiffGate        │
│   no filesystem real                            │
└─────────────────────┬───────────────────────────┘
                      │ Result
                      ▼
              ┌──────────────┐
              │  OSOutcome   │
              └──────────────┘
```

### PROTOCOLO SEND (Multi-IA Handoff)
Configuração persistente de autoridades por shell. Cada shell pode ter MÚLTIPLAS IAs com pesos:

```json
{
  "shell3": {
    "autoridades": [
      {"ia": "claude", "modelo": "claude-sonnet-4", "peso": 0.60},
      {"ia": "gemini", "modelo": "gemini-3.5-flash", "peso": 0.25},
      {"ia": "gpt", "modelo": "gpt-5.5", "peso": 0.15}
    ],
    "modo": "consenso"  // ou "paralelo", "sequencial", "best-of-n"
  },
  "shell2": {
    "autoridades": [
      {"ia": "mecanico", "modelo": "deepseek-v4-flash", "peso": 0.50},
      {"ia": "claude", "modelo": "claude-haiku-4.5", "peso": 0.50}
    ],
    "modo": "sequencial"
  },
  "shell1": {
    "autoridades": [
      {"ia": "ollama", "modelo": "qwen3.5:4b", "peso": 0.70},
      {"ia": "gemini", "modelo": "gemini-3.5-flash", "peso": 0.30}
    ],
    "modo": "fallback"
  }
}
```

## Setup

### 1. Ollama (Shell 1 — Execução Local)
```bash
# Instalar: https://ollama.com/download/windows
# Verificar versão:
ollama --version    # v0.30.7 ou superior

# Iniciar servidor:
ollama serve
# OU instalar como serviço Windows (recommended):
# Ollama > Settings > "Run on startup"

# Baixar modelos:
ollama pull qwen3.5:4b            # ~2.5GB — roteador + tarefas simples
ollama pull north-mini-code       # coding local (quando disponível GGUF)
ollama pull llama3.2:3b           # alternativa leve (~2GB)

# Verificar modelos baixados:
ollama list
```

### 2. Workbench AI.Manager
```bash
cd D:\projetos\workbench-ai.manager
pip install -r requirements.txt
python WorkbenchWebUI.py     # NiceGUI web UI na porta 8080

# Verificar 164 testes:
python -m pytest tests/ -v --tb=short
```

### 3. Integração Hermes
O pipeline é chamado via Python do Hermes. Criar script que importa o orquestrador:

```python
from workbench.core.orchestrator_multi import WorkbenchOrchestratorMulti
from workbench.core.orchestrator import OSRequest

orch = WorkbenchOrchestratorMulti()  # Carrega PROTOCOLO SEND
req = OSRequest(objective="seu objetivo", target_files=[...])
outcome = orch.run_multi(req)
```

## Token Tracking & Report — Novo!

Após cada tarefa, o Hermes agora gera automaticamente um relatório de tokens/custo.

Arquivo: `src/workbench/monitoring/token_tracker.py`

```python
from workbench.monitoring.token_tracker import TaskTracker

t = TaskTracker()
t.start_task("Nome da tarefa")
t.record("Shell 3 (Decisão)", "gpt-4o-mini", prompt_tokens=..., completion_tokens=..., elapsed_ms=...)
t.record("Shell 1 (Execução)", "qwen2.5-coder:7b (local)", prompt_tokens=..., completion_tokens=...)
t.finish()
print(t.report())       # Relatório completo formatado
print(t.summary_line()) # Linha resumo para embedar
```

Histórico persistido em: `runtime/token_history.jsonl`

### Custo por modelo (tabela de preços atualizada)

| Modelo | Input/1K | Output/1K | 
|--------|---------|----------|
| GPT-4o-mini | $0.00015 | $0.00060 |
| deepseek-v4-flash | $0.00030 | $0.00120 |
| Claude Sonnet 4 (fronteira) | $0.00300 | $0.01500 |
| Ollama/Mecânico (local) | **grátis** | **grátis** |

A economia é calculada vs o modelo fronteira (Claude Sonnet 4).

## Pontos de Integração com Hermes

| Componente Workbench | Equivalente Hermes | Ponte |
|---------------------|-------------------|-------|
| Shell 3 (decisão) | Hermes Agent (modelo atual) | Hermes decide se delega para Workbench |
| Shell 1 (Ollama) | Terminal → `ollama run` | Script Python via terminal() |
| MCP (filesystem) | write_file / patch tools | Workbench MCP → Hermes tools |
| Memory (workbench_core.db) | memory tool + session_search | Bridge: Hermes lê/grava na DB |
| Audit log | — | Workbench audit_log é independente |
| Token compression | — | workbench.core.token_compressor |

## Arquivos de Referência

| Arquivo | Conteúdo |
|---------|----------|
| `D:\projetos\workbench-ai.manager\AGENTS.md` | Documentação completa da arquitetura (29KB) |
| `D:\projetos\workbench-ai.manager\CLAUDE_HANDOFF_v9.md` | Handoff protocol v9 industrial |
| `D:\projetos\workbench-ai.manager\src\workbench\shells\shell3_multi.py` | Multi-adapter decisor |
| `D:\projetos\workbench-ai.manager\src\workbench\shells\protocol_send_config.py` | Config PROTOCOLO SEND |
| `D:\projetos\workbench-ai.manager\src\workbench\core\orchestrator_multi.py` | Orquestrador multi-shell |
| `D:\projetos\workbench-ai.manager\src\workbench\core\diff_gate.py` | Validador AST + segurança |
| `D:\projetos\workbench-ai.manager\runtime\protocol_send_config.json` | Config persistente |

## ⚠️ Pitfalls

### Ollama não está rodando
```bash
# Verificar:
ollama list    # se falhar → servidor não está rodando
# Iniciar:
ollama serve
# OU verificar serviço Windows: Services.msc → Ollama → Start
```

### PROTOCOLO SEND não configurado
O WebUI tem aba "⚙️ Autoridade" para configurar. Alternativamente, editar:
`D:\\\\projetos\\\\workbench-ai.manager\\\\runtime\\\\protocol_send_config.json`

### 🔴 Conhecido: Orquestrador Parado (desde 17/05/2026)

O orquestrador multi-shell `WorkbenchOrchestratorMulti` apresenta 3 falhas conhecidas:

1. **Shell 1 (Ollama/execução):** 10 workers configurados, mas TODAS as execuções históricas retornam resultados vazios (`"todas_falharam"`). O adapter `shell1_multi` não conecta corretamente à API Ollama — provável erro de endpoint ou timeout.

2. **Shell 3 (Decisão):** O detector de código no output do LLM é excessivamente agressivo. TODAS as execuções históricas foram rejeitadas com `"REJEITADO: código detectado"` mesmo quando o LLM só deu uma resposta textual. O regex do `reject_if_code()` em `shell3_multi.py` precisa ser ajustado.

3. **API Keys:** O config `protocol_send_config.json` aponta para `gpt-4o-mini` + `OPENAI_API_KEY`, mas a chave pode não estar configurada no `.env.production`.

**Diagnóstico rápido:**
```bash
# Verificar se há locks (0 = parado)
ls runtime/locks/

# Últimas execuções
tail -1 runtime/shell3_multi_executions.jsonl | python -m json.tool

# Verificar se Ollama responde
curl http://127.0.0.1:11434/api/tags
```

### ⚠️ Pitfall: Ollama não está rodando

### Shell 3 não deve retornar código
⚠️ REGRA ABSOLUTA: Shell 3 (decisão) JAMAIS retorna código. `reject_if_code()` bloqueia na saída. A implementação do adapter deve chamar esta função.

### Dependências opcionais para Shell 3 real
```bash
pip install anthropic              # Claude adapter
pip install google-generativeai   # Gemini adapter
pip install openai                 # OpenAI + Grok adapters
```

## 🛡️ Hermes Watchdog — Anti-Travamento (24/7 Automático)

### Instalação Única
```bash
# 1. Criar atalho na inicialização do Windows (não precisa de admin):
powershell -ExecutionPolicy Bypass -File "D:\projetos\hermes-watchdog\create_startup_shortcut.ps1"

# 2. Iniciar agora:
D:\projetos\hermes-watchdog\watchdog_hermes.bat
```

O instalador:
1. Cria atalho em `shell:startup\HermesWatchdog.lnk` → inicia com o login do Windows
2. Inicia o watchdog imediatamente em background
3. **Nunca mais você precisa pensar nisso** — roda 24/7

> **Nota:** O watchdog usa `.bat` em vez de `.ps1` porque o terminal MSYS/bash do Hermes expande `$env:VAR` incorretamente. O `.bat` não tem esse problema.

### O que o Watchdog Monitora
| Condição | Gatilho | Ação |
|----------|---------|------|
| Log do Hermes parado >25min | Stale log | taskkill /F + recovery |
| Processo zumbi (5+ min rodando sem load) | CPU detection | taskkill /F + recovery |

### Recuperação Automática
Quando watchdog detecta travamento:
1. `taskkill /F` no Hermes travado
2. Limpa locks órfãos do Workbench (`runtime/locks/`)
3. Deixa pronto para restart limpo
4. Perda máxima: **25 minutos** (vs 65min sem watchdog)

### Arquitetura de Proteção (3 camadas)

```
CAMADA 1: Windows Startup (ao fazer login)
└── HermesWatchdog.lnk → cmd.exe → watchdog_hermes.bat
    └── Verifica Hermes a cada 5 min
    └── Detecta log parado >25 min → taskkill + recovery

CAMADA 2: Cron Hermes (a cada 5 min)
└── watchdog_guardian.bat (no_agent, script)
    └── Se watchdog não está rodando → reinicia

CAMADA 3: Manual / Diagnóstico
└── Verificar: cat ~/hermes-watchdog/watchdog_state.json
└── Logs: cat ~/hermes-watchdog/logs/watchdog_*.log
```

### Como Verificar o Status
```powershell
# Se watchdog está rodando:
Get-ChildItem "$env:USERPROFILE\hermes-watchdog\watchdog_state.json" | Get-Content

# Últimos logs:
Get-ChildItem "$env:USERPROFILE\hermes-watchdog\logs\" | Sort-Object LastWriteTime -Desc | Select-Object -First 1 | Get-Content

# Verificar atalho na inicialização:
Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\HermesWatchdog.lnk"
```

### ⚠️ Pitfall: PowerShell + MSYS/bash no Windows
O terminal do Hermes roda **git-bash (MSYS)**, não PowerShell nativo. Isso causa:

1. **`$env:VARNAME` é comido pelo bash**: `powershell -Command "echo $env:USERPROFILE"` imprime `:USERPROFILE` porque bash expande `$env` para vazio.
   - **Solução:** Use `.bat` em vez de `.ps1` para scripts autônomos, ou escape com `\$env:VARNAME`.

2. **Operador ternário do PS7 não funciona**: `$cond ? "a" : "b"` só existe no PowerShell 7. No PS5.1 (Windows 10 padrão), use `if/else`.
   - **Solução:** Sempre use `if/else` em scripts PowerShell no Windows.

3. **`cmd.exe /C` é mais seguro que `Start-Process`**: Para iniciar processos em background do Hermes, use `cmd.exe /c "comando"` via `terminal(background=true)`.

### 📋 Comandos Rápidos

### Iniciar Tudo (ordem correta sem watchdog já iniciando sozinho)
```bash
# 1. Verificar se watchdog já está rodando
cat ~/hermes-watchdog/watchdog_state.json

# 2. Iniciar Ollama (IA local) - se necessário
ollama serve

# 3. Workbench WebUI (opcional — PROTOCOLO SEND)
cd D:/projetos/workbench-ai.manager && python WorkbenchWebUI.py
```

### Parada Segura
```bash
# Limpar locks órfãos se pipeline for interrompido
rm -rf ~/AppData/Local/hermes/cron/* 2>/dev/null
rm -rf /d/projetos/workbench-ai.manager/runtime/locks/* 2>/dev/null
```

## Mandato de Inovação
Este pipeline é a BASE para implementar ferramentas, técnicas e workflows identificados pelo `index-news-daily` (ver MANDATO DE INOVAÇÃO ATIVA naquele skill). Quando algo implementável é detectado nas notícias:
1. Analisar compatibilidade com o pipeline Workbench
2. Propor extensão (novo adapter, novo módulo core, novo MCP tool)
3. Implementar mediante autorização

## Formato Padrão de Comunicação (TODOS os cards)
Use o formato Hermes 2.0 definido no skill `index-news-daily`:
- `📰 A notícia:` — breve, 1-2 frases, fato central
- `💡⚡ O que muda no seu código:` — didático, lucidativo, com siglas explicadas, ação + solução
- NUNCA usar "Explicação rápida" ou "Impacto no Dev" separados
