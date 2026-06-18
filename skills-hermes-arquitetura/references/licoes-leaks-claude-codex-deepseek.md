# Lições Aplicáveis dos Leaks — Claude Code + Codex + DeepSeek

## 1. Claude Code — 512K linhas via npm source map (31 Mar 2026)

**Repositório de system prompts vazados**: https://github.com/asgeirtj/system_prompts_leaks (43.3K ★)
**Repositório do código vazado**: https://github.com/chauncygu/collection-claude-code-source-code

### Descobertas Arquiteturais

#### O Agent Loop é Simples (20 linhas)
```typescript
while (true) {
  const response = await model.generate(messages);
  if (!response.hasToolCall()) break;
  const result = await executeTool(response.toolCall);
  messages.push(response, result);
}
```
**Toda complexidade (512K linhas) está no harness**: permissões, contexto, memória, compressão, schemas.

#### Segurança na Tool, não em Policy
Regras de segurança (git, filesystem, rede) estão **dentro da descrição da tool** que o modelo lê:

> Bash tool description: "NUNCA rode git push --force, reset --hard, checkout . a menos que o usuário peça explicitamente"

Isso é mais efetivo que policy externa porque o modelo vê a regra no momento da decisão.

#### Multi-Agente via Prompt, não Framework
Claude Code implementa multi-agente **inteiramente via system prompt** — sem LangGraph, CrewAI, AutoGen.
> "Anthropic warns that frameworks obscure the prompts that matter"

#### KV Cache Compartilhado
Sub-agents clonam KV cache do parent, economizando 40-60% em tokens de contexto.

#### 44 Features Escondidas
Compile-time flags: undercover mode (remove branding de commits), sandbox mode, auto-commit naming, etc.

#### Cheap Model para Cheap Decisions
Claude Code usa **Haiku** (modelo mais barato) para **safety checks** antes de executar comandos sensíveis. Só sobe pra Opus quando precisa de reasoning pesado.

### Aplicação Imediata no Hermes
- ✅ Loop PEV implementado (`auto-executor`)
- ✅ Haiku = DeepSeek V4 Flash (nosso `roteador-economico`)
- ✅ KV cache sharing = `delegate_task` batch (tasks[])
- ✅ Segurança na tool = descrever regras nas skills
- ✅ Context eng. > prompt eng. = skills separam instrução fixa de conteúdo variável
- ❌ Falta: hooks pre/post tool (parcial no Hermes)

---

## 2. OpenAI Codex — Architectural Deep Dive (Jan-Jun 2026)

**Fonte**: https://openai.com/index/unrolling-the-codex-agent-loop/
**Prompt leak**: https://blog.promptlayer.com/how-openai-codex-works-behind-the-scenes/

### Estrutura do Prompt do Codex

OpenAI publicou o *Codex Prompting Guide* que revela:

#### Autonomy Directive (Diretiva-Chave)
``` 
The model should implement with reasonable assumptions rather than asking clarifying questions.
Once given a direction, it should proactively gather context, plan, implement, test, and refine.
```
**Essa é a diretiva mais impactante.** Sem ela, o modelo pede permissão a cada passo.

#### Tool Preference Hierarchy
- Preferir `apply_patch` sobre shell commands para edição de arquivos
- Evitar `sed`, `awk`, `echo >>` — frágeis e difíceis de auditar

#### Parallel Tool Calling
```
Think first about all needed resources, then batch all calls together.
```

#### Two Personality Modes
- **Builder mode** (default): mãos-livres, autonomia máxima
- **Reviewer mode**: modo de análise, só lê, não edita (similar ao nosso `Explore` do Claude)

#### Symphony — Orquestrador Multi-Agente (Abr 2026)
https://openai.com/index/open-source-codex-orchestration-symphony/
- Board (Linear) → control plane para coding agents
- Cada ticket vira um agente → agentes rodam continuamente → humanos revisam PRs
- **Hermes Kanban faz exatamente isso**

### Aplicação no Hermes
- ✅ Autonomy directive = `output-coeso` + `auto-executor`
- ❌ Parallel tool calling = Hermes já faz (multi_tool_use)
- ✅ Symphony = Hermes Kanban já implementa
- ❌ Tool preference hierarchy = podemos documentar nas skills qual tool preferir

---

## 3. DeepSeek V4 — Engram Architecture (Papers Dez 2025-Jan 2026)

**Fonte**: https://www.digitalapplied.com/blog/deepseek-v4-engram-architecture-coding-model-guide

### Engram Memory ≠ RAG
- RAG: busca vetorial externa (O(n) na busca)
- Engram: **memória condicional aprendida** — o modelo decide quando lembrar, O(1) em inferência
- Equivalente Hermes: skills + memory fazem papel similar, mas de forma mais explícita

### CSA (DeepSeek Sparse Attention)
- Atenção esparsa que escala pra 1M tokens
- Equivalente: nossa compressão de contexto (threshold: 0.35)

### V4 Flash vs V4 Pro
- Flash: 284B params, 13B ativos, $0.15/1M → **nosso padrão**
- Pro: 1.6T params, 49B ativos, $0.50/1M → só se Flash falhar 3x

---

## Resumo — O que implementar AGORA

| Lição | Origem | Implementação |
|-------|--------|--------------|
| Loop simples (while + tool calls) | Claude Code | `auto-executor` ✅ |
| Cheap model p/ cheap decisions | Claude Code | `roteador-economico` ✅ |
| KV cache compartilhado | Claude Code | `delegate_task` batching ✅ |
| Segurança na tool desc | Claude Code | Adicionar nas skills 📝 |
| Autonomy directive | Codex | `output-coeso` ✅ |
| Symphony = Kanban | Codex | Já temos 📝 |
| Engram = Skills + Memory | DeepSeek | Já temos ✅ |
| Contexto 1M + CSA | DeepSeek | Compressão config ✅ |
