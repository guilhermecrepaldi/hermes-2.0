# System Prompt Vazado do Claude Code (Fable 5 — versão 2.1.172)

**Fonte**: https://github.com/asgeirtj/system_prompts_leaks (43.3K stars)
**Data do leak**: 31 Mar 2026 (código via npm source map) + system prompt extraído continuamente
**Modelo**: Claude Fable 5 (capturado em 11 Jun 2026)

---

## Estrutura do System Prompt

O prompt de sistema do Claude Code é dividido em seções claras:

### 1. Identidade
```
You are Claude Code, Anthropic's official CLI for Claude.
You are an interactive agent that helps users with software engineering tasks.
```

### 2. Harness Instructions
- Texto fora de tool use aparece pro usuário como markdown
- Ferramentas rodam atrás de permissão; chamada negada = usuário recusou — ajustar, não repetir
- `<system-reminder>` tags são injetadas pelo harness, não pelo usuário
- Preferir ferramentas dedicadas a shell commands quando possível
- Referenciar código como `file_path:line_number`

### 3. Comunicação com o Usuário
- Escrever como se fosse pra um colega que saiu e está voltando
- Texto entre tool calls pode não ser mostrado ao usuário
- Tudo que o usuário precisa deve estar na MENSAGEM FINAL (sem tool call depois)
- **Lead with outcome**: primeira frase responde "o que aconteceu"
- Legibilidade > Concisão
- Frases completas, sem abreviações ou jargão
- Tabelas só para fatos enumeráveis

### 4. Regras de Código
- Código deve ler como o código ao redor
- Comentário só para restrição que o código não pode mostrar
- **Nunca** comentar "de onde veio", "o que a próxima linha faz", "por que a mudança está correta"

### 5. Segurança e Destrutividade
- Ações irreversíveis: confirmar antes
- Enviar conteúdo para serviço externo = publicar (pode ser cacheado/indexado)
- Antes de deletar/sobrescrever: verificar se o alvo corresponde ao que foi descrito
- Reportar resultados fielmente: se teste falha, dizer com output

### 6. Modelo (Fable 5)
```
This iteration of Claude is Claude Fable 5, the first model in Anthropic's new Claude 5 family...
```

### 7. Context Management
- Quando a conversa cresce, contexto é sumarizado automaticamente
- Quando tem info suficiente, agir — não re-derivar fatos já estabelecidos
- **Operando autonomamente**: usuário não está assistindo, não pode responder perguntas no meio da tarefa
- Não perguntar "quer que eu...?" — agir
- Parar só para ações destrutivas ou mudanças de escopo genuínas

### 8. Regra de Ouro
```
Before ending your turn, check your last paragraph. If it is a plan, an analysis, 
a question, a list of next steps, or a promise about work you have not done 
('I'll...', 'let me know when...'), do that work now with tool calls.
End your turn only when the task is complete or you are blocked on input only 
the user can provide.
```

### 9. Ferramentas

O Claude Code expõe **menos de 20 tools por padrão** (até 60+ total):
- Agent (spawn sub-agents)
- AskUserQuestion (perguntas ao usuário)
- Bash (terminal)
- Read (leitura de arquivos)
- WebFetch (fetch de URL)
- WebSearch (busca web)
- Edit (edição de arquivos)
- Write (escrita de arquivos)
- NotebookEdit
- ExitPlanMode
- E outras

Cada tool tem **descrições extensas com regras de segurança embutidas**.

---

## Lições para o Hermes

1. **Lead with outcome**: nossa skill `output-coeso` já implementa (diagnóstico → ação → resultado)
2. **Não perguntar, agir**: nossa skill `auto-executor` faz isso (só pergunta no PLAN)
3. **Segurança na tool desc**: podemos adicionar regras de segurança nas descrições das tools via config
4. **Context compressão automática**: Hermes já faz com `compression.enabled: true`
5. **Mensagem final sem tool call**: nosso output-coeso garante isso
6. **Modelo barato para decisões baratas**: Claude usa Haiku para safety checks — nosso `roteador-economico` faz similar
