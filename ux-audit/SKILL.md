---
name: ux-audit
description: "UX Audit Agent - inspirado no Framer 3.0 Agents. Analisa a interface real da aplicacao, aponta inconsistencias visuais, de spacing, cor, tipografia e acessibilidade. Agents trabalham no canvas, nao no chat."
category: creative
tags: [ux, design, audit, framer, vision, quality, accessibility]
---

# UX Audit Agent

## Identidade

Inspirado no Framer 3.0 Agents (jun/2026): "Agents trabalham no canvas - nao no chat."
Este agente nao gera snippets desconectados. Ele analisa a interface real, identifica problemas visuais e propoe correcoes aplicaveis diretamente no codigo.

## Fluxo de Auditoria UX

1. Navegar para a aplicacao (browser_navigate)
2. Capturar screenshot (browser_vision)
3. Analisar visual contra taste-skill + design-system
4. Verificar:
   a. Consistencia de cores (variaveis CSS do tema)
   b. Espacamento e alinhamento
   c. Tipografia (escala, contraste, hierarquia)
   d. Acessibilidade (contraste, labels, foco)
   e. Responsividade (breakpoints)
   f. Consistencia de componentes (botoes, inputs, cards)
5. Gerar relatorio com:
   - Screenshots anotadas
   - Problemas encontrados (por severidade)
   - Sugestoes de correcao com CSS exato
   - Referencia visual desejada

## Checklist de Auditoria

### 1. Cores e Tema
- Usa variaveis CSS (var(--bg), var(--fg), etc) em vez de cores hardcoded?
- Contraste suficiente entre bg/fg? (ratio min 4.5:1 para texto normal)
- Cores de estado (success, error, warning) sao distintas e reconheciveis?
- Modo escuro/claro respeita as mesmas variaveis?
- Nao ha mais de 3 cores de destaque (accent) competindo?

### 2. Espacamento e Layout
- Padding/margin seguem uma escala consistente? (4, 8, 12, 16, 20, 24, 32, 48)
- Elementos alinhados vertical/horizontalmente?
- Altura minima de alvos de clique? (min 44px recomendado)
- Grid/espacamento entre cards e secoes uniforme?
- Nao ha overflow horizontal ou elementos cortados?

### 3. Tipografia
- Tamanhos de fonte seguem escala? (12, 13, 14, 16, 18, 20, 22, 24, 28, 32)
- Hierarquia clara: headings > subheadings > body > caption?
- Line-height adequado? (1.4-1.6 para body, 1.2-1.3 para headings)
- Peso (font-weight) consistente? (400 body, 600 sub, 700 heading)
- Nao ha mais de 2 familias de fonte?

### 4. Acessibilidade
- Elementos interativos tem :focus visible?
- Botoes tem cursor: pointer?
- Labels associados a inputs?
- Icones com aria-label ou texto alternativo?
- Contraste de texto sobre imagens/fundos?

### 5. Componentes
- Todos os botoes tem mesma altura, padding, border-radius?
- Inputs tem mesma altura e estilo de borda?
- Cards tem mesmo padding e sombra?
- Transicoes sao consistentes? (mesma duracao e easing)
- Scrollbars personalizadas ou default?

## Como Usar

```bash
# Auditoria completa de uma pagina
1. browser_navigate(url)
2. browser_vision(question="Analise a interface contra o checklist de UX")
3. Para cada item do checklist, verificar visualmente
4. Gerar relatorio com screenshots + correcoes CSS

# Auditoria rapida (componente especifico)
1. browser_navigate(url + "#secao")
2. browser_vision(question="Analise apenas o componente X")
3. Relatorio focado naquele componente

# Audit de consistencia (multiplas paginas)
1. browser_navigate(url + "/page1")
2. browser_vision(question="Checklist UX item 1-3")
3. browser_navigate(url + "/page2")
4. browser_vision(question="Checklist UX item 1-3")
5. Comparar screenshots e apontar inconsistencias
```

## Integracao com Skills Existentes

| Skill | Como usa no UX Audit |
|---|---|
| taste-skill | Regras de qualidade aplicadas a CSS/HTML |
| design-system-references | 54 referencias de design para comparacao |
| browser_vision | Captura e analisa a tela real |
| spec-agent | Gera SPEC de correcao baseada no relatorio |
| stack-docs | Documentacao de componentes |
| auto-executor | Loop de correcao: detecta > propoe > aplica > verifica |

## Exemplo de Saida

```
=== UX AUDIT REPORT ===
Pagina: CodeWriter /lesson/1
Severidade: MEDIA (3 issues)

1. [ALTA] Contraste insuficiente no .overview-stat
   - Atual: color var(--fg-dim) sobre var(--bg)
   - Ratio ~3.8:1 (minimo 4.5:1)
   - Correcao: usar var(--fg) ou aumentar opacity

2. [MEDIA] Altura de clique no .overview-close
   - Atual: sem min-width/min-height declarados
   - Correcao: min-width:44px; min-height:44px;

3. [BAIXA] Borda inconsistente nos cards
   - .overview-block usa border:1px solid var(--border)
   - .final-review-card usa mesma borda sem padding uniforme
   - Sugestao: unificar padding dos cards em 24px

=== SCREENSHOT: [path] ===
```
