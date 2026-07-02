# 🎯 Estratégia de Entrevista — NowPro Technology & Solutions

## Roteiro Completo de Perguntas e Observações

---

## Parte 1 — Perguntas Pra ELES (o que você precisa saber)

### 🟢 Bloco 1: Produto e Código (abertura)

> *"Eu estudei o site de vocês, as 7 soluções. Pra entender melhor como posso contribuir desde o começo, queria entender como está a arquitetura hoje."*

| # | Pergunta | O que você descobre | Resposta esperada vs Alerta |
|:-:|----------|---------------------|-----------------------------|
| 1 | **"O código atual foi construído por consultoria externa ou pelo time interno?"** | Se dependem de terceiros | "Sim, Plataformatec/Rondy" → precisam internalizar |
| 2 | **"O time interno tem acesso completo ao repositório e pode fazer deploy sem depender de ninguém?"** | Autonomia real do time | Se "precisa do Rondy" = dependência crítica |
| 3 | **"Qual é a stack atual do backend? Ruby, Python, outro?"** | Se vão migrar ou manter | Ruby = legado pra reescrever. Python = seu território |
| 4 | **"O código tem testes automatizados? CI/CD rodando?"** | Maturidade de engenharia | Se não tem = caos. Se tem = estruturado |
| 5 | **"Qual foi o último deploy em produção e quem fez?"** | Quem realmente opera o sistema | Se foi o Rondy = dependência |

### 🔵 Bloco 2: Time e Processo (meio)

> *"Entendendo melhor como o time funciona hoje..."*

| # | Pergunta | O que você descobre |
|:-:|----------|---------------------|
| 6 | **"Quantas pessoas no time de tecnologia hoje? Quais os papéis?"** | Se precisa de liderança técnica |
| 7 | **"Como funciona o processo de desenvolvimento? Sprint? Kanban?"** | Maturidade do processo |
| 8 | **"Quem faz code review hoje? Quem define arquitetura?"** | Lacuna de revisão técnica |
| 9 | **"O Rondy ainda está envolvido? Qual a dedicação dele?"** | Se a dependência é ativa ou já acabou |
| 10 | **"Qual a maior dor do time hoje? O que trava entrega?"** | Problema real que você vai resolver |

### 🟣 Bloco 3: Dados e Infraestrutura (fechamento)

> *"Agora sobre a parte que mais me interessa — os dados..."*

| # | Pergunta | O que você descobre |
|:-:|----------|---------------------|
| 11 | **"Como vocês consultam o DataJud hoje? API direta, Elasticsearch, middleware?"** | Nível de sofisticação da integração |
| 12 | **"Têm API Key do DataJud ativa? Qual tribunal mais consultam?"** | Se pipeline já existe ou é do zero |
| 13 | **"Como tratam LGPD nos dados dos processos? Anonimizam antes de enviar pra IA?"** | Maturidade de compliance |
| 14 | **"Qual provedor de IA usam? OpenAI, Claude, próprio?"** | Stack de IA atual |
| 15 | **"Onde roda a aplicação hoje? Render, AWS, próprio?"** | Stack de infraestrutura |

---

## Parte 2 — Respostas Que Você PREPARA Antes

### Pra cada pergunta deles, sua resposta pronta:

| Pergunta deles | Sua resposta |
|----------------|-------------|
| **"Fala sobre sua experiência"** | *"Tenho experiência construindo pipelines de dados do zero. Meu último projeto foi um sistema que recebe diretrizes determinísticas, orquestra APIs externas, executa processamento local e devolve relatórios estruturados — similar ao que vocês fazem com DataJud + IA. A diferença é que meu domínio não era jurídico, mas o padrão arquitetural é o mesmo."* |
| **"Já trabalhou com DataJud?"** | *"Estudei a fundo. O DataJud expõe índices Elasticsearch. Cada tribunal tem seu próprio padrão de índice. A consulta é via POST /{indice}/_search com queries booleanas. Já tenho uma spec de pipeline com cache Redis, circuit breaker por tribunal, retry com backoff, e fallback entre tribunais. É o que eu implementaria primeiro aqui."* |
| **"E com LLMs/IA?"** | *"Sim. Trabalho com LLMs locais e cloud. Pra vocês, o ideal é cloud (OpenAI/Claude) pra produção, com anonimização LGPD antes de enviar. Tenho experiência com RAG, embeddings e pipelines de IA determinísticos."* |
| **"É presencial em SP?"** | *"Sim, Parque Ibirapuera é tranquilo pra mim."* |
| **"Qual sua pretensão?"** | *"Prefiro entender primeiro o escopo e a autonomia da posição. Mas pra uma posição de engenheiro sênior que vai estruturar o pipeline de dados do zero, minha referência é entorno de R$ 12-16k PJ. Mas podemos conversar."_* |

---

## Parte 3 — Observações de Comportamento

### O que observar NA ENTREVISTA

| Sinal | Interpretação |
|-------|--------------|
| **Não sabem responder sobre o código** (quem fez, onde tá, como deploya) | Produto 100% terceirizado, vão te jogar no caos |
| **Falam muito em "plano" e pouco em "código"** | Startup early-stage, produto é mais marketing que realidade |
| **Jefferson/Maicon estão na sala** e não falam | Time inseguro, você vai ser o líder técnico de fato |
| **Rondy está na entrevista** | A dependência é real. Se ele está avaliando, o código é dele |
| **Perguntam de disponibilidade pra começar "ontem"** | Desespero. Use a seu favor na negociação |
| **Falam em "reescrever tudo"** | Código legado é insustentável. Sinal VERMELHO (ou oportunidade, depende) |

### O que você NÃO deve falar

```
❌ "Vi que o GitHub de vocês é fraco"
   → Soa arrogante. Em vez disso:
   ✅ "Estruturei meu pipeline de dados como spec. Posso compartilhar."

❌ "Rondy tá desatualizado"
   → O cara pode ser amigo deles. Em vez disso:
   ✅ "Qual a relação de vocês com a Plataformatec hoje?"

❌ "Isso aqui é fácil de fazer"
   → Subestima o problema. Em vez disso:
   ✅ "Tenho experiência com esse tipo de integração. Posso estruturar."
```

---

## Parte 4 — Pós-Entrevista

### Se passar, seu plano de 90 dias:

```
SEMANA 1-2:
├── Acessar repositório
├── Entender o código existente
├── Mapear arquitetura atual
├── Identificar gargalos
└── Plano de ação pro pipeline

SEMANA 3-4:
├── Pipeline DataJud rodando (busca CPF/CNPJ)
├── BrasilAPI integrada (CNPJ real)
├── Cache + rate limit
├── Swagger documentado
└── PRIMEIRA ENTREGA

SEMANA 5-8:
├── Webhooks (monitoramento de processos)
├── NLP service (anonimização LGPD)
├── Testes automatizados
├── CI/CD pipeline
└── SEGUNDA ENTREGA

SEMANA 9-12:
├── IA service (sumarização + classificação)
├── Integração com frontend
├── Documentação técnica do pipeline
├── Mentoria do time interno
└── TERCEIRA ENTREGA
```

---

## Parte 5 — Checklist Pré-Entrevista

- [ ] Ler a spec `REFERENCIA_COMPLETA.md` (41KB, 11 seções)
- [ ] Ter na ponta da língua: o que é DataJud, Elasticsearch, BrasilAPI, LegalNLP
- [ ] Preparar 2 minutos de pitch pessoal
- [ ] Decorar as 15 perguntas (seção 1)
- [ ] Ter respostas pras perguntas comuns (seção 2)
- [ ] Saber o salário pretendido (R$ 12-16k PJ)
- [ ] Levar um case: "Em 1 mês entrego a Nowpro Busca"
