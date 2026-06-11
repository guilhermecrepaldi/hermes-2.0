# Edition Isolation (Multi-Tab Card Filtering)

## Problema
O HTML gerado pelo cron NÃO aninha cards dentro de `<div class="tab-content">`. Em vez disso, cada `<article class="news-card">` é irmão solto da `<section>`, não filho. Isso significa que `activeTab.querySelectorAll('.news-card')` só encontra o primeiro card (o único dentro de `<section>`).

## Solução JS Runtime
No handler de troca de aba (`initTabs`), adicione:

```javascript
document.querySelectorAll('.news-card').forEach(c => {
  const id = c.getAttribute('data-id') || '';
  const matches = id.startsWith('hw-' + ed) || id.startsWith('arc-' + ed) || 
                  id.startsWith('app-' + ed) || id.startsWith('str-' + ed) ||
                  ed === 'aovivo-001';
  c.style.display = matches ? '' : 'none';
});
```

**Como funciona:**
- Cada card tem `data-id` no formato `{secao}-{edicao}-{numero}` (ex: `hw-001-01`, `arc-002-03`)
- Ao trocar para ed-002: busca cards com prefixo `hw-002`, `arc-002`, etc.
- Cards que não correspondem recebem `display: none`
- Na aba Ao Vivo (`ed === 'aovivo-001'`): mostra TODOS os cards

## Mesmo filtro no Teleprompter
```javascript
const activeEd = document.querySelector('.tab-btn.active')
  ?.getAttribute('data-ed') || '001';
const cards = Array.from(document.querySelectorAll('.news-card')).filter(c => {
  const id = c.getAttribute('data-id') || '';
  return id.startsWith('hw-' + activeEd) || id.startsWith('arc-' + activeEd)
      || id.startsWith('app-' + activeEd) || id.startsWith('str-' + activeEd);
});
```

## Live SEO por Edição
A função `updateLiveSEO(ed)` gera metadados (título, descrição, tags) baseados nos cards da edição ativa:

```javascript
const seoEd = ed === 'aovivo-001' ? (window._lastEd || '001') : ed;
updateLiveSEO(seoEd);
window._lastEd = seoEd;
```

`window._lastEd` guarda a última edição visitada. Quando a aba Ao Vivo é clicada, o SEO mantém os dados da última edição que o usuário estava vendo.

## Verificação
- [ ] Ao clicar Ed. 002, cards Ed. 001 somem (display:none)
- [ ] Ao voltar para Ed. 001, cards Ed. 002 somem
- [ ] Checkbox/localStorage funciona por edição
- [ ] Ticker mostra títulos da edição ativa
- [ ] Teleprompter mostra cards da edição ativa
- [ ] Ao Vivo mantém SEO da última edição
