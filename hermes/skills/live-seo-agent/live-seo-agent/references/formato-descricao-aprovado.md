# Formato de Descrição YouTube SEO — APROVADO PELO USUÁRIO

Este é o FORMATO EXATO que o usuário validou e exige. Qualquer variação será rejeitada.

## Descrição Completa (liveDescFull)

```
🔴 TOP OF THE HOUR - IA | QUINTA-FEIRA, 11 DE JUNHO DE 2026

Nesta edição:
▸ 🔴 HARDWARE (7): Blackwell Ultra Entrega 50x Performance, e LG Group Anunciam Parceria para AI Fac, Chip Quântico Majorana 2 com Qubits Topo, Assina Primeiro Acordo de Datacenter de IA, Protestos Contra Datacenters, Kolmogorov-Arnold Networks em FPGAs, Fornece Confidential Computing
▸ 🟠 ARQUITETURA (11): DiffusionGemma, ReasonAlloc, Leva 20B Parâmetros para o Dispositivo, Agents' Last Exam, EEVEE, Lente Unificadora SFT, Regularização de Divergência RL, Fala Full-Duplex, OpenCV 5 com CUDA, Apache Burr, Critic Visual Fundamentado
▸ 🟢 APPS (10): Claude Fable 5 Mythos, OpenAI Superapp, Cohere North Mini Code, Harness-1 Search, Gemini Agêntica, Siri Reformulada, Oasis 3, Conway Plataforma, Amazon Alexa AI Stack, DeepSeek SGLang
▸ 🔵 ESTRATÉGIA (8): IPO Anthropic $350B, OpenAI Reestruturação, Regulação Alemanha, RSI 8x código, Meta Open-Weight, DeepSeek vs GPT, Warner + Sureel AI, Google Supercomputador

📢 INSCREVA-SE para não perder nenhuma edição!
👍 Deixe seu like — ajuda o algoritmo a levar conhecimento a mais engenheiros.
💬 Comente: qual notícia te impactou mais?

⚠️ Jornal técnico independente. Análise baseada em dados e fontes abertas. Verifique informações em fontes oficiais.
```

## Primeiras 2 Linhas (liveDescTop — aparecem no search)

```
🔴 TOP OF THE HOUR - IA | 10 JUN 2026 | Análise técnica das 36 principais notícias de Inteligência Artificial. NVIDIA Blackwell Ultra 50x, DiffusionGemma 4x, Claude Fable 5 Mythos e IPO da Anthropic de $350B. Nesta edição: 7 Hardware, 11 Arquitetura, 10 Apps, 8 Estratégia — a cascata completa do engenheiro.
```

## Título SEO (liveTitulo)

```
🔴 TOP OF THE HOUR - IA: Blackwell Ultra, DiffusionGemma & IPO Anthropic
```

Regras do título:
- 40-60 caracteres
- Palavra-chave nos primeiros 30 caracteres
- 1-2 emojis (🔴 para lives, 📡 para notícias)
- Formato: `🔴 [MARCA]: [GANCHO 1], [GANCHO 2] & [GANCHO 3]`
- Ganchos: extrair das 3 primeiras notícias, remover prefixos de empresa

## Tags (liveTags)

```
TOP OF THE HOUR, IA, inteligência artificial, engenharia de IA, NVIDIA Blackwell, Anthropic, Claude Fable 5, OpenAI, Google DeepMind, DiffusionGemma, machine learning, live engenharia, tecnologia, IPO
```

Regras:
- 10-15 tags
- Primeiras: broad (IA, inteligência artificial)
- Meio: específicas do conteúdo (NVIDIA, Blackwell, Claude Fable 5)
- Fim: contexto (machine learning, live engenharia)
- NUNCA: Hermes Agent, Nous Research, nome da ferramenta

## Thumbnail (liveThumb)

```
Fundo escuro gradiente (#0a0a0f → #1a1a28). Texto grande: "BLACKWELL · FABLE 5 · IPO" em dourado. Badge "AO VIVO" vermelho no canto superior direito. Logos NVIDIA + Anthropic no canto inferior. 1280×720px.
```

## Geração Dinâmica no JS

A função `updateLiveSEO(ed)` no HTML gera estes metadados automaticamente:

```javascript
// Hook: extrair números (50x, $350B, 4x) para a primeira linha
const extractNum = (t) => {
  const m = t.match(/(\d+[xX%]|\$\d+[BMK])/);
  return m ? m[1] : '';
};

// Formatar cada notícia: remover empresa + verbo, manter conceito
const formatNews = (titles) => titles.map(t => {
  let core = t.split(':')[0].split('—')[0].trim();
  core = core.replace(/^(NVIDIA|Google|Apple|Microsoft|Meta|Anthropic|OpenAI|DeepSeek)\s*/i, '');
  core = core.replace(/^(Novo|Nova|Novos|Novas)\s+/i, '');
  core = core.replace(/^(Lanç[ao]|Anuncia|Apresenta|Chegou|Revela)\s+/i, '');
  return core.trim().substring(0, 40);
}).filter(Boolean).join(', ');
```
