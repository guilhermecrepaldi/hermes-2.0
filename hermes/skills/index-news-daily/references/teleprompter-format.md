# Teleprompter — Build & Format Reference

## Como o teleprompter funciona

O modo teleprompter (📺 no ticker do rodapé) cria um overlay fullscreen para apresentação ao vivo.

## Extração de conteúdo

Cada card no teleprompter extrai:

1. **Título**: `card.querySelector('h3').textContent` — 42px, bold
2. **Descrição**: `card.querySelector('.detail-content')` — texto completo do formato "📰 A notícia"
3. **Impacto**: Do mesmo `.detail-content`, parte após "💡⚡" — texto do formato "O que muda no seu código"
4. **Logo**: `card.querySelector('.brand-logo')?.src` — path do arquivo (para o apresentador)
5. **Badge**: `card.querySelector('.imp-badge')` — nível de importância

**⚠️ NUNCA usar `.news-card-fact` ou `.impact-text` para a descrição do teleprompter.** 
Estes campos são ocultos e contêm apenas texto semântico curto. O teleprompter DEVE extrair do `.detail-content` (o mesmo conteúdo do expandível "▶ Ler explicação").

### Lógica de split (para separar descrição do impacto):

```javascript
const detailContent = card.querySelector('.detail-content');
let descText = '';
let impactText = '';
if (detailContent) {
  const full = detailContent.textContent.trim();
  const partes = full.split(/💡⚡|⚡/);
  if (partes.length > 1) {
    descText = partes[0].replace('📰 A notícia:', '').replace('📰 A notícia', '').trim();
    impactText = partes[partes.length - 1]
      .replace('O que muda no seu código:', '')
      .replace('O que muda no seu código', '').trim();
  } else {
    descText = full; // sem split se não encontrar marcador
  }
}
```

### Fallback (quando .detail-content não existe):
```javascript
if (!descText) {
  const fe = card.querySelector('.news-card-fact');
  if (fe) descText = fe.textContent.trim();
}
if (!impactText) {
  const ie = card.querySelector('.impact-text');
  if (ie) impactText = ie.textContent.trim();
}
```

## Filtro por edição ativa

O teleprompter usa o `data-ed` do botão de aba ativo para filtrar cards. **⚠️ CRÍTICO: Se a aba ativa for "🎙️ Ao Vivo", usa `window._lastEd` (a última edição real) — NÃO o data-ed do botão.** O data-ed da aba Ao Vivo é `aovivo-001`, que não corresponde a nenhum prefixo de card real.

```javascript
const activeBtn = document.querySelector('.tab-btn.active');
const rawEd = activeBtn ? activeBtn.getAttribute('data-ed') : '001';
const activeEd = rawEd === 'aovivo-001' ? (window._lastEd || '001') : rawEd;
const cards = Array.from(document.querySelectorAll('.news-card')).filter(c => {
  const id = c.getAttribute('data-id') || '';
  return id.startsWith('hw-' + activeEd) || id.startsWith('arc-' + activeEd)
      || id.startsWith('app-' + activeEd) || id.startsWith('str-' + activeEd);
});
```

Isso garante que cards de ed-001 NÃO apareçam quando ed-002 estiver ativa, e que o teleprompter funcione mesmo quando acionado da aba Ao Vivo.

⚠️ **NÃO usar tab-content.active para filtrar cards.** A estrutura HTML gerada pelo cron coloca cards como irmãos das seções, NÃO filhos do tab-content. O único filtro confiável é `data-id` prefix match contra o `data-ed` do botão ativo (ou `_lastEd`).

## SEM cortes de texto

O teleprompter exibe o texto COMPLETO do `detail-content`. **NUNCA truncar com `substring()` ou `.slice()`.** O scroll é gerenciado pelo wrapper `.tele-cards-scroll` com `overflow-y: auto`.

```javascript
// ✅ CERTO — texto completo:
div.innerHTML = '<div class="tele-content">' + descText + '</div>'

// ❌ ERRADO — texto cortado:
div.innerHTML = '<div class="tele-content">' + descText.substring(0, 400) + '</div>'
```

## Responsividade (CSS)

Os tamanhos de fonte usam `clamp()` para adaptar a qualquer resolução:

```css
.tele-title { font-size: clamp(28px, 4vw, 52px); }    /* mínimo 28, pref 4vw, max 52 */
.tele-content { font-size: clamp(18px, 2.2vw, 28px); }
.tele-impact { font-size: clamp(16px, 1.8vw, 24px); }
```

O overlay tem um wrapper scrollável para evitar overflow:

```html
<div class="tele-cards-scroll" id="teleCardsScroll">  <!-- flex:1 + overflow-y:auto -->
  <div id="teleCards"></div>
</div>
```

Header (contador + fechar), progress bar e hint são `flex-shrink: 0` — sempre visíveis. Apenas o conteúdo do card rola.

## Navegação

| Tecla | Ação |
|-------|------|
| Espaço / → / ↓ | Próxima notícia |
| ← / ↑ | Notícia anterior |
| Esc | Fechar teleprompter |
| Clique na tela | Próxima notícia |

## O overlay não fecha?

Se o botão ✕ não fechar, o problema é que `closeTeleprompter` não está acessível no escopo global no momento do parse HTML. Soluções:
1. Usar `window.closeTeleprompter` na definição da função
2. No `onclick`, usar `window.closeTeleprompter()`

## Formato de cada card no overlay

```
─────────────────────────────────────────
🔥 Crítico                                1/36
                                     [✕ Esc]

NVIDIA Blackwell Ultra Entrega 50x
Performance para IA Agêntica
         ↑ título 42px

NVIDIA anunciou o Blackwell Ultra — GPU
focada em cargas agênticas...
         ↑ conteúdo 24px (do detail-content)

⚡ O gargalo deixa de ser a GPU e passa
a ser o orquestrador...
         ↑ impacto 20px (do detail-content)

📁 https://www.nvidia.com/logo.png
         ↑ path do logo (para o apresentador)

─────────────────────────────────────────
[████████··························]  3%
Espaço / → Próxima · ← Anterior · Esc Sair
```
