# 📚 JUS PLATFORM — Dicionário Técnico & Referência Arquitetural (PaaS)

> **Clean Room Spec** — Jul/2026. 100% original.
> Síntese de: DataJud CNJ, LegalNLP, BrasilAPI, Direito Lux MVP, ECC Agent OS.
> **Arquitetura: Platform as a Service (PaaS) — API-first, multi-tenant, escalável.**
> Para pesquisa, estudo, entrevistas e implementações futuras.

---

## Índice

1. [Glossário Jurídico-Técnico](#1-glossário-jurídico-técnico)
2. [APIs e Endpoints](#2-apis-e-endpoints)
3. [Modelo de Domínio Unificado](#3-modelo-de-domínio-unificado)
4. [Arquitetura PaaS](#4-arquitetura-paas)
5. [Tribunais Brasileiros — Catálogo Completo](#5-tribunais-brasileiros)
6. [NLP Jurídico Brasileiro](#6-nlp-jurídico-brasileiro)
7. [Boas Práticas e Padrões](#7-boas-práticas-e-padrões)
8. [Stack Recomendada](#8-stack-recomendada)
9. [Features e Produtos](#9-features-e-produtos)
10. [Plano de Monetização](#10-plano-de-monetização)
11. [Referências e Fontes](#11-referências-e-fontes)

---

## 1. Glossário Jurídico-Técnico

### Termos Jurídicos

| Termo | Definição |
|-------|-----------|
| **DataJud** | Base nacional de dados judiciais do CNJ (Conselho Nacional de Justiça). Contém todos os processos ativos do país, indexados em Elasticsearch. |
| **Numeração Única** | Formato `NNNNNNN-DD.AAAA.T.RRRR.NNNNN` — identificador único de processo judicial brasileiro. |
| **DJE / DJ** | Diário da Justiça Eletrônico — publicação oficial de atos processuais. |
| **PJe** | Processo Judicial Eletrônico — sistema usado pela maioria dos tribunais brasileiros. |
| **ESAJ** | Sistema de acompanhamento processual do TJSP (Tribunal de Justiça de São Paulo). |
| **Parte** | Pessoa física ou jurídica envolvida em um processo (autor, réu, terceiro). |
| **Movimentação** | Cada ato ou evento registrado no andamento processual. |
| **Andamento** | Conjunto de movimentações de um processo ao longo do tempo. |
| **Classe** | Categoria do processo (ex: "Procedimento Comum Cível", "Execução Fiscal"). |
| **Assunto** | Matéria jurídica do processo (árvore hierárquica CNJ). |
| **Instância** | Grau de jurisdição: 1º grau (vara), 2º grau (tribunal), STJ/STF. |
| **Precatório** | Requisição de pagamento contra a Fazenda Pública, após decisão judicial definitiva. |
| **RPV** | Requisição de Pequeno Valor — precatório de até 60 salários mínimos. |
| **SISBAJUD** | Sistema de bloqueio de valores judicial (antigo BACENJUD). |
| **CNJ** | Conselho Nacional de Justiça — órgão de controle administrativo do Poder Judiciário. |
| **Tabelas Processuais Unificadas (TPU)** | Padronização CNJ de classes, assuntos, movimentos e fases processuais. |

### Termos Técnicos

| Termo | Definição |
|-------|-----------|
| **Elasticsearch (ES)** | Motor de busca e indexação usado pelo DataJud para armazenar e consultar processos. |
| **Índice ES** | Coleção de documentos no Elasticsearch. Cada tribunal tem seu próprio padrão de índice. |
| **Query Bool** | Tipo de query ES que combina `must`, `should` e `filter` para buscas complexas. |
| **Circuit Breaker** | Padrão de resiliência: se um serviço falha N vezes seguidas, bloqueia requisições por um período. |
| **Cache Key** | Hash único que identifica uma consulta. `sha256(f"{api_key}:{tipo}:{tribunal}:{parametros}")`. |
| **Sliding Window** | Algoritmo de rate limit que conta requisições em uma janela temporal deslizante. |
| **Backoff Exponencial** | Estratégia de retry: delay aumenta progressivamente (1s, 3s, 5s...). |
| **Stale-while-revalidate** | Estratégia de cache: serve conteúdo velho enquanto atualiza em background. |
| **Anonimização** | Substituição de dados sensíveis por tokens genéricos para cumprir LGPD. |
| **Mascaramento RegEx** | Técnica de substituição de padrões via expressões regulares (CPF → `[documento]`). |
| **Falha Recuperável** | Erro temporário que justifica retry: timeout, 5xx, conexão recusada. |
| **Falha Permanente** | Erro que não deve ser retentado: 400, 401, 403, 404. |
| **API Key** | Chave de autenticação para consumir a plataforma. Gerada por app/usuário. |
| **Quota** | Limite de consumo por API Key (requisições/dia, req/min, endpoints disponíveis). |
| **Planos** | Tier de serviço: Free, Pro, Business, Enterprise — cada um com quotas diferentes. |
| **Webhook** | Callback HTTP que a plataforma chama quando um evento ocorre (ex: nova movimentação). |
| **Data Enrichment** | Enriquecimento de dados: cruzar DataJud + BrasilAPI + LGPD para gerar insights. |

### Termos PaaS

| Termo | Definição |
|-------|-----------|
| **Control Plane** | Camada de gerenciamento: cadastro de apps, API keys, quotas, billing, dashboard. |
| **Data Plane** | Camada de execução: processamento de requisições, cache, upstream calls. |
| **Gateway** | Ponto único de entrada da plataforma. Roteia, autentica, rate-limit, loga. |
| **App** | Aplicação cliente que consome a plataforma. Tem seu próprio API Key e quota. |
| **Tenant Isolation** | Isolamento de dados entre apps: app A não vê dados do app B. |
| **Usage Metering** | Medição de consumo por API Key para billing. |
| **Developer Hub** | Portal do desenvolvedor: docs, SDKs, playground, dashboard. |

---

## 2. APIs e Endpoints

### 2.1 Padrão de Endpoint

```
https://api.jusplatform.com/{produto}/{versao}/{recurso}

Headers obrigatórios:
  X-API-Key:     {api_key_da_app}
  Content-Type:  application/json

Resposta padrão:
  {
    "success": true,
    "data": { ... },
    "meta": {
      "request_id": "uuid",
      "processing_time_ms": 234,
      "credits_used": 1,
      "credits_remaining": 999
    }
  }
```

### 2.2 Catálogo de APIs

#### 🏛️ Produto: JUD (Dados Processuais)

| Endpoint | Versão | Descrição | Créditos |
|----------|:------:|-----------|:--------:|
| `GET /jud/v1/processos/{numero}` | v1 | Dados completos de um processo | 1 |
| `GET /jud/v1/processos/{numero}/movimentacoes` | v1 | Movimentações de um processo | 1 |
| `GET /jud/v1/processos/{numero}/partes` | v1 | Partes de um processo | 1 |
| `POST /jud/v1/processos/lote` | v1 | Consulta em lote (até 50) | 10 |
| `GET /jud/v1/busca?documento={cpf/cnpj}` | v1 | Busca processos por CPF/CNPJ | 2 |
| `GET /jud/v1/busca?nome={nome_parte}` | v1 | Busca processos por nome | 3 |
| `GET /jud/v1/tribunais` | v1 | Lista tribunais disponíveis | 0 |

**Cache (server-side):** 30min a 2h dependendo do recurso.

#### 🏢 Produto: EMP (Dados de Empresas)

| Endpoint | Versão | Descrição | Créditos |
|----------|:------:|-----------|:--------:|
| `GET /emp/v1/cnpj/{cnpj}` | v1 | Dados completos da empresa | 1 |
| `GET /emp/v1/cnpj/{cnpj}/socios` | v1 | Quadro societário | 1 |
| `POST /emp/v1/cnpj/lote` | v1 | Consulta CNPJ em lote (até 50) | 10 |
| `GET /emp/v1/cep/{cep}` | v1 | Endereço por CEP | 0 |

**Cache (server-side):** 24h a 48h.

#### 🤖 Produto: NLP (Processamento de Texto Jurídico)

| Endpoint | Versão | Descrição | Créditos |
|----------|:------:|-----------|:--------:|
| `POST /nlp/v1/limpar` | v1 | Limpeza e normalização de texto jurídico | 1 |
| `POST /nlp/v1/anonimizar` | v1 | Anonimização LGPD de texto jurídico | 2 |
| `POST /nlp/v1/extrair` | v1 | Extração de entidades (OAB, valores, prazos) | 2 |
| `POST /nlp/v1/classificar` | v1 | Classificação de peça processual | 3 |
| `POST /nlp/v1/sumarizar` | v1 | Sumarização de andamento/decisão | 3 |
| `POST /nlp/v1/gerar` | v1 | Geração de minuta de petição | 5 |

**Cache:** Não aplicável (cada requisição é única).

#### 📊 Produto: SCORE (Análise Inteligente)

| Endpoint | Versão | Descrição | Créditos |
|----------|:------:|-----------|:--------:|
| `POST /score/v1/risco-processual` | v1 | Score de risco de um processo | 5 |
| `POST /score/v1/similaridade` | v1 | Similaridade entre casos | 3 |
| `GET /score/v1/jurimetria/{tribunal}/{classe}` | v1 | Estatísticas por tribunal/classe | 10 |
| `POST /score/v1/prever-resultado` | v1 | Predição de resultado | 10 |

#### ⚙️ Produto: ADMIN (Gerenciamento da Plataforma)

| Endpoint | Versão | Autenticação | Descrição |
|----------|:------:|:------------:|-----------|
| `GET /admin/v1/usage` | v1 | API Key + User | Consulta de consumo |
| `GET /admin/v1/quotas` | v1 | API Key + User | Limites do plano |
| `POST /admin/v1/webhooks` | v1 | API Key + User | Gerenciar webhooks |
| `GET /admin/v1/logs` | v1 | API Key + User | Logs de requisições |
| `GET /admin/v1/health` | v1 | Pública | Status da plataforma |

### 2.3 Webhooks

Notificações push quando eventos ocorrem:

```
POST {url_do_cliente}/webhook/jud/movimentacao
  Body: {
    "event": "jud.movimentacao",
    "data": {
      "processo": "NNNNNNN-DD.AAAA.T.RRRR.NNNNN",
      "tribunal": "TJSP",
      "movimentacao": { ... },
      "timestamp": "2026-07-02T10:00:00Z"
    }
  }

Eventos disponíveis:
  jud.movimentacao        → Nova movimentação em processo monitorado
  jud.prazo_proximo       → Prazo processual se aproximando
  emp.cnpj_alterado       → Dados cadastrais mudaram
  nlp.processado          → Processamento NLP concluído
```

### 2.4 Fontes de Dados (Upstreams)

| Fonte | URL | Uso | Cache | Cobertura |
|-------|-----|:---:|:-----:|:---------:|
| DataJud ES | `POST /{indice}/_search` | Processos judiciais | 30min | Nacional |
| BrasilAPI | `GET /api/cnpj/v1/{cnpj}` | CNPJ via minhareceita | 24h | Nacional |
| BrasilAPI | `GET /api/cep/v1/{cep}` | CEP multi-provider | 48h | Nacional |
| OpenCEP | `GET /v1/{cep}` | CEP fallback | 48h | Nacional |
| ViaCEP | `GET /ws/{cep}/json` | CEP fallback 2 | 48h | Nacional |
| Ollama | `POST /api/chat` | IA local (LGPD) | N/A | Local |
| LegalNLP | pip package | NLP jurídico | N/A | Python |
| BERTikal | HuggingFace | Classificação BERT | N/A | Modelo |

---

## 3. Modelo de Domínio Unificado

### 3.1 Arquitetura de Entidades (PaaS Context)

```
┌─────────────────────────────────────────────────────────────────┐
│                        SISTEMA JUS PLATFORM                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  CONTROL PLANE                          │   │
│  │                                                         │   │
│  │  Apps/Clientes ──├── Planos ──├── API Keys ──├── Quotas│   │
│  │  Billing ──├── Usage ──├── Webhooks ──├── Logs        │   │
│  │  Developer Hub ──├── Docs ──├── SDKs                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     DATA PLANE                          │   │
│  │                                                         │   │
│  │  Gateway ──├── Auth ──├── Rate Limit ──├── Router      │   │
│  │                                                         │   │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────────┐ │   │
│  │  │ JUD  │ │ EMP  │ │ NLP  │ │SCORE │ │   ADMIN      │ │   │
│  │  │ Svc  │ │ Svc  │ │ Svc  │ │ Svc  │ │   Svc        │ │   │
│  │  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──────────────┘ │   │
│  │     │        │        │        │                        │   │
│  │     ▼        ▼        ▼        ▼                        │   │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                  │   │
│  │  │Redis │ │Redis │ │Ollama│ │pgvec │                  │   │
│  │  │Cache │ │Cache │ │Local │ │tor   │                  │   │
│  │  └──────┘ └──────┘ └──────┘ └──────┘                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Entidades do Sistema

```typescript
// ──── CONTROL PLANE ────

interface App {
  id: UUID
  nome: string
  descricao?: string
  plano_id: UUID
  ativo: boolean
  created_at: datetime
  owner_id: UUID       // Usuário dono da app
}

interface Plano {
  id: UUID
  nome: string          // Free, Pro, Business, Enterprise
  precos: Preco[]       // Por período/mês
  quotas: Quota[]       // Limites por produto
  features: string[]    // Produtos disponíveis
}

interface APIKey {
  key: string           // jwt_sk_live_xxxx ou jwt_sk_test_xxxx
  app_id: UUID
  ambiente: 'test' | 'live'
  ativo: boolean
  created_at: datetime
  ultimo_uso?: datetime
}

interface Quota {
  produto: 'jud' | 'emp' | 'nlp' | 'score'
  requests_per_minute: number
  requests_per_day: number
  cache_enabled: boolean
  webhooks_enabled: boolean
}

interface UsageRecord {
  id: UUID
  api_key_id: UUID
  app_id: UUID
  endpoint: string
  produto: string
  credits_used: number
  status_code: number
  processing_time_ms: number
  created_at: datetime
}

interface Webhook {
  id: UUID
  app_id: UUID
  url: string
  eventos: string[]     // ["jud.movimentacao", "jud.prazo_proximo"]
  ativo: boolean
  ultimo_disparo?: datetime
  ultimo_erro?: string
}

// ──── DATA PLANE ────

interface Request {
  id: UUID
  api_key: string
  endpoint: string
  params: object
  produto: string
  timestamp: datetime
}

interface Response {
  success: boolean
  data: object | null
  error?: {
    code: string
    message: string
    details?: object
  }
  meta: {
    request_id: UUID
    processing_time_ms: number
    credits_used: number
    credits_remaining: number
    cached: boolean
    source?: string       // datajud, brasileapi, ollama
  }
}

interface CacheEntry {
  key: string
  value: object
  ttl: number
  created_at: datetime
  api_key_id?: UUID      // Namespace por app
}
```

### 3.3 Modelo de Dados (Processo Judicial)

```typescript
interface Processo {
  numero: string            // NNNNNNN-DD.AAAA.T.RRRR.NNNNN
  encontrado: boolean
  classe: string            // Código + descrição
  assunto: object           // Árvore CNJ
  tribunal: string          // TJSP, TRF1...
  situacao: string          // Em andamento, Arquivado, Suspenso
  instancia: 1 | 2
  data_ajuizamento: string  // ISO date
  data_ultima_atualizacao: string // ISO datetime
  valor_causa?: number
  segredo_justica: boolean
  partes: Parte[]
  movimentacoes?: Movimentacao[]
}

interface Parte {
  tipo: 'PESSOA_FISICA' | 'PESSOA_JURIDICA'
  nome: string
  documento: string         // CPF/CNPJ
  papel: string             // AUTOR, REU, TERCEIRO, ADVOGADO
  advogado?: {
    nome: string
    oab: string
    uf: string
  }
}

interface Movimentacao {
  sequencia: number
  data: string              // ISO datetime
  codigo: string            // Código CNJ do movimento
  descricao: string
  complemento?: string
  sigiloso: boolean
  valor?: number
}

interface Tribunal {
  codigo: string            // TJSP, TRF1, TRT2...
  nome: string
  indice_es: string         // api_publica_tjsp
  tipo: TribunalTipo
  regiao: string
  ativo: boolean
}

type TribunalTipo =
  | 'supremo' | 'superior' | 'federal'
  | 'estadual' | 'trabalho' | 'eleitoral' | 'militar'

interface Empresa {
  cnpj: string
  razao_social: string
  nome_fantasia?: string
  situacao: string
  endereco: {
    logradouro: string
    numero: string
    bairro: string
    cidade: string
    uf: string
    cep: string
  }
  cnae: string
  capital_social: number
  socios: Array<{
    nome: string
    qualificacao: string
  }>
  porte: 'ME' | 'EPP' | 'DEMAIS'
}
```

---

## 4. Arquitetura PaaS

### 4.1 Control Plane vs Data Plane

```
                    PLANO DE CONTROLE
┌──────────────────────────────────────────────────────────────┐
│  Developer Hub (Next.js)                                     │
│  ├── Cadastro/Login                                          │
│  ├── Dashboard de consumo                                    │
│  ├── Gerenciamento de API Keys                               │
│  ├── Webhook Config                                          │
│  ├── Playground (testar endpoints)                           │
│  └── Documentação interativa                                 │
│                                                              │
│  Admin API (FastAPI CRUD)                                    │
│  ├── /apps          → CRUD apps                              │
│  ├── /api-keys      → CRUD chaves                            │
│  ├── /plans         → CRUD planos                            │
│  ├── /usage         → Consulta consumo                       │
│  └── /webhooks      → CRUD webhooks                          │
│                                                              │
│  Billing Service                                             │
│  ├── Stripe/Asaas integration                                │
│  ├── Invoice generation                                      │
│  └── Usage metering → billing                                │
└──────────────────────────────────────────────────────────────┘
                              │
                    chamadas internas (gRPC/REST)
                              │
                              ▼
                      PLANO DE DADOS
┌──────────────────────────────────────────────────────────────┐
│  API Gateway (FastAPI)                                       │
│  ├── Roteamento: /jud/v1/* → JUD Service                    │
│  ├── Autenticação: validar API Key                          │
│  ├── Rate Limit: sliding window por key                     │
│  ├── Cache: Redis (s-maxage)                                │
│  ├── Logging: structured JSON                                │
│  └── CORS: configurável por app                              │
│                                                              │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌───────────┐        │
│  │ JUD    │  │ EMP    │  │ NLP    │  │ SCORE     │        │
│  │Service │  │Service │  │Service │  │Service    │        │
│  ├────────┤  ├────────┤  ├────────┤  ├───────────┤        │
│  │DataJud │  │Brasil  │  │LegalNLP│  │Ollama +   │        │
│  │ES Query│  │API     │  │+Ollama │  │pgvector   │        │
│  │Circuit │  │Cache   │  │Process │  │Embeddings │        │
│  │Breaker │  │24h     │  │Pipeline│  │Search     │        │
│  └────────┘  └────────┘  └────────┘  └───────────┘        │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Fluxo de Requisição

```
CLIENTE: GET https://api.jusplatform.com/jud/v1/processos/NNN...NN
  Headers: { X-API-Key: "jus_sk_live_xxxxx" }
  │
  ▼
1. API GATEWAY
  ├── [Middleware] Log: request_id=uuid, timestamp
  ├── [Middleware] CORS: verificar origin permitida
  ├── [Middleware] Auth: validar API Key no Redis (cache 5min)
  │   ├── App ID → buscar plano → verificar quotas
  │   └── Se inválida → 401 { error: "API_KEY_INVALIDA" }
  ├── [Middleware] Rate Limit: INCR chave no Redis
  │   ├── Chave: "ratelimit:{app_id}:{produto}:minuto:{minuto_atual}"
  │   ├── Se excedeu → 429 { error: "RATE_LIMIT_EXCEDIDO" }
  │   └── TTL: 60s
  ├── [Middleware] Cache: verificar GET
  │   ├── Chave: "cache:{produto}:{app_id}:{parametros_hash}"
  │   ├── Se existe e TTL > 0 → retornar 200 (cache hit)
  │   └── Anotar: veio_do_cache=true
  └── [Router] Direcionar para JUD Service
  │
  ▼
2. JUD SERVICE (processo handler)
  ├── [Validar] Formato do número do processo
  │   └── Inválido → 400 { error: "NUMERO_PROCESSO_INVALIDO" }
  ├── [Circuit Breaker] state = FECHADO?
  │   ├── ABERTO → 503 { error: "TRIBUNAL_INDISPONIVEL" }
  │   └── MEIO-ABERTO → permitir 1, medir resultado
  ├── [Tribunal Mapper] código → índice ES
  │   └── Inválido → 400 { error: "TRIBUNAL_INVALIDO" }
  ├── [Query Builder] montar JSON ES Query DSL
  ├── [Execução] POST {base_url}/{indice}/_search
  │   ├── Timeout 30s → retry (max 3, backoff 1s/3s/5s)
  │   ├── Falha permanente (4xx) → erro sem retry
  │   └── Falha todas tentativas → 502 { error: "FONTE_EXTERNA_INDISPONIVEL" }
  ├── [Parser] extrair hits → Processo domain object
  │   └── Resposta vazia → 404 { error: "PROCESSO_NAO_ENCONTRADO" }
  └── [Circuit Breaker] registrar sucesso/falha
  │
  ▼
3. API GATEWAY (pós-processamento)
  ├── [Cache] Store: redis.setex(chave_cache, ttl, resposta_serializada)
  ├── [Usage] Record: registrar consumo (1 crédito)
  │   ├── Redis: INCR "usage:{app_id}:{produto}:{dia}"
  │   └── Async: enviar para fila de persistência (evitar bottleneck)
  └── [Response] 200 + JSON padronizado + meta
  │
  ▼
CLIENTE: Recebe resposta
```

### 4.3 Política de Retry (DataJud)

```
Tentativa 0: delay 0s
Tentativa 1: delay 1s
Tentativa 2: delay 3s
Tentativa 3: delay 5s (máximo)

✅ RETENTAR:
  Timeout de conexão, Timeout de leitura
  HTTP 500, 502, 503, 504
  Erro de DNS, Conexão recusada

❌ NÃO RETENTAR:
  HTTP 400 (Bad Request)
  HTTP 401/403 (Auth)
  HTTP 404 (Not Found)
  HTTP 429 (Too Many Requests)
```

### 4.4 Circuit Breaker (por tribunal + por app)

```
Por tribunal:   TJSP tem seu próprio breaker
Por app:        App A não afeta App B

FECHADO ──5 falhas consecutivas──▶ ABERTO
  ▲                                   │
  │                                   │
  └──3 sucessos seguidos── MEIO-ABERTO◀──30 segundos
```

### 4.5 Cache Strategy

```
Chave: "cache:{produto}:{namespace}:{tipo}:{parametros_hash}"
Namespace por API Key / App (isolamento entre clientes)

TTL:
  Processo (completo):      30min
  Movimentações:            15min
  Partes:                   2h
  CNPJ:                     24h
  CEP:                      48h
  Resultados NLP:           N/A (não cachear)
  Classificação/Sumário:    1h (se mesmo input)
```

### 4.6 Rate Limiting (por API Key)

```
Plano Free:
  JUD:   10 req/min,   500 req/dia
  EMP:   30 req/min,  1000 req/dia
  NLP:   5 req/min,    100 req/dia

Plano Pro:
  JUD:   60 req/min,  5000 req/dia
  EMP:   120 req/min, 10000 req/dia
  NLP:   30 req/min,  1000 req/dia
  SCORE: 10 req/min,  500 req/dia

Plano Business:
  JUD:   300 req/min, 50000 req/dia
  EMP:   600 req/min, 100000 req/dia
  NLP:   120 req/min, 5000 req/dia
  SCORE: 60 req/min,  3000 req/dia

Enterprise: Sob consulta (ilimitado)
```

### 4.7 Webhooks Architecture

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐
│  DataJud │    │  JUD Service │    │ Webhook      │
│  ES Query│───▶│  detecta     │───▶│ Dispatcher   │
└──────────┘    │  mudança     │    └──────┬───────┘
                └──────────────┘           │
                                           ▼
                                    ┌──────────────┐
                                    │  Redis Queue  │
                                    │  (retry 3x)   │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  POST {url}   │
                                    │  do cliente   │
                                    └──────────────┘

Tentativas de entrega: 0s, 60s, 300s (3x)
Se todas falharem: marcar webhook como "erro" + log
```

---

## 5. Tribunais Brasileiros

### 5.1 Catálogo Completo

**Superiores (5):**

| Código | Nome | Índice ES | Região |
|--------|------|-----------|--------|
| STF | Supremo Tribunal Federal | `api_publica_stf` | BR |
| STJ | Superior Tribunal de Justiça | `api_publica_stj` | BR |
| TST | Tribunal Superior do Trabalho | `api_publica_tst` | BR |
| TSE | Tribunal Superior Eleitoral | `api_publica_tse` | BR |
| STM | Superior Tribunal Militar | `api_publica_stm` | BR |

**Federais (6):**

| Código | Índice ES | Abrangência |
|--------|-----------|-------------|
| TRF1 | `api_publica_trf1` | AC, AM, AP, BA, DF, GO, MA, MG, MT, PA, PI, RO, RR, TO |
| TRF2 | `api_publica_trf2` | ES, RJ |
| TRF3 | `api_publica_trf3` | MS, SP |
| TRF4 | `api_publica_trf4` | PR, RS, SC |
| TRF5 | `api_publica_trf5` | AL, CE, PB, PE, RN, SE |
| TRF6 | `api_publica_trf6` | MG |

**Estaduais (27):** TJAC a TJTO → `api_publica_{codigo_lower}`

**Trabalhistas (24):** TRT01 a TRT24 → `api_publica_trt{NN}`

**Eleitorais (27):** TREAM a TRETO → `api_publica_tre{uf}`

**Militares (3):** TJMSP, TJMMG, TJMRS

### 5.2 Resolução de Código

```
Entrada: "TJSP", "tjsp", "TJ SP"
  → normalizar: maiúsculas, sem espaços, sem caracteres especiais
  → buscar no registry: TJSP → encontrado
  → retornar índice: api_publica_tjsp

Entrada: "TRT1", "TRT01"
  → tentar formato com/sem zero → TRT01 = TRT1
  → retornar índice: api_publica_trt01

Não encontrado?
  → tentar códigos alternativos (sem zero, com zero)
  → erro 400: TRIBUNAL_INVALIDO
```

---

## 6. NLP Jurídico Brasileiro

### 6.1 Pipeline de Limpeza

```
TEXTO JURÍDICO BRUTO
  │
  ▼ [ftfy] Correção Unicode
  │   ├── caracteres corrompidos (ã, ç, é)
  │   └── encoding misto
  │
  ▼ Normalização
  │   ├── quebras de linha → espaços
  │   ├── múltiplos espaços → simples
  │   └── lowercasing (opcional)
  │
  ▼ Mascaramento RegEx (tokens)
  │   ├── [url]:      http\S+ | www\S+
  │   ├── [email]:    [^\s]+@[^\s]+
  │   ├── [oab]:      OAB\s?[:-]?\d+\s?/?\s?[A-Z]+
  │   ├── [data]:     \d{2}\s?\/\s?\d{2}\s?\/\s?\d{4}
  │   ├── [processo]: \d{15,} (15+ dígitos)
  │   ├── [valor]:    R\s?\$\s?\d+[.,]?\d*
  │   └── [numero]:   \d+
  │
  ▼ Pós-processamento
  │   ├── siglas sem pontos (C.P.F → CPF)
  │   ├── plurais/gênero ((s), (a), (o))
  │   └── hífens (arquivem - se → arquivem-se)
  │
  ▼ TEXTO LIMPO + Dict com entidades extraídas
```

### 6.2 Aplicações de NLP (como Produto)

| Produto API | Input | Output | Engine | Créditos |
|-------------|-------|--------|--------|:--------:|
| `POST /nlp/v1/limpar` | Texto jurídico | Texto limpo | Python + RegEx | 1 |
| `POST /nlp/v1/anonimizar` | Texto com dados | Texto anonimizado | RegEx + Ollama | 2 |
| `POST /nlp/v1/extrair` | Texto jurídico | Entidades (OAB, valores) | RegEx + Ollama | 2 |
| `POST /nlp/v1/classificar` | Peça processual | Tipo da peça | BERTikal / Ollama | 3 |
| `POST /nlp/v1/sumarizar` | Decisão/andamento | Resumo 3 parágrafos | Ollama | 3 |
| `POST /nlp/v1/gerar` | Template + dados | Minuta de petição | Ollama + template | 5 |

### 6.3 Modelos Pré-Treinados

| Modelo | Tipo | Params | Acesso |
|--------|------|:------:|--------|
| **BERTikal** | BERT-base jurídico português | 110M | HuggingFace: `felipemaiapolo/legalnlp-bert` |
| **Word2Vec CBOW/SG** | Embeddings (100d) | ~200MB | Figshare + `get_premodel('wodc')` |
| **FastText CBOW/SG** | Embeddings sub-word (100d) | ~200MB | Figshare + `get_premodel('fasttext')` |
| **Phraser** | Detecção de bigramas | ~5MB | Figshare + `get_premodel('phraser')` |
| **qwen2.5-coder:7b** | LLM generalista | 7B | Ollama local |
| **NeuralMind BERT** | BERT-base português geral | 110M | NeuralMind AWS S3 |

### 6.4 Anonimização LGPD (Camada Obrigatória)

```
Antes de qualquer processamento por LLM externa:

1. Rodar pipeline LegalNLP de mascaramento
2. Substituir:
   ├── CPF:     ***.000.000-**
   ├── CNPJ:    **.000.000/****-**
   ├── Nome:    "[PARTE_AUTORA]" / "[PARTE_REU]"
   ├── OAB:     "[OAB]"
   ├── Endereço: "[ENDEREÇO]"
   ├── Telefone: "[TELEFONE]"
   └── Email:   "[EMAIL]"
3. Apenas texto anonimizado vai para LLM externo
4. Ollama local processa dados reais (não sai da máquina)
```

### 6.5 Instalação LegalNLP

```bash
pip install legalnlp

from legalnlp.clean_functions import clean

texto = "O autor, CPF 000.000.000-00, propõe..."
result = clean(texto, lower=True, return_masked=True)
# {'txt': 'o autor [documento] propoe ...',
#  'oab': [], 'data': [], 'processo': [],
#  'valor': [], 'numero': ['000','000','000','00']}
```

---

## 7. Boas Práticas e Padrões

### 7.1 Padrões de Projeto (PaaS Context)

| Padrão | Quando usar | Exemplo JUS |
|--------|-------------|-------------|
| **Proxy API Gateway** | Ponto único de entrada | Gateway com auth + rate limit + cache |
| **Backend for Frontend** | Múltiplos tipos de cliente | SDK JavaScript vs API REST |
| **Circuit Breaker** | Serviço upstream instável | DataJud por tribunal |
| **Retry com Backoff** | Falhas transitórias | DataJud timeout |
| **Cache-Aside** | Dados pouco voláteis | CNPJ, CEP, dados de processo |
| **Strangler Fig** | Migração de versão de API | JUD v1 → v2 |
| **Event Sourcing** | Audit trail de requisições | Usage records |
| **Queue-Based Load Leveling** | Webhook delivery | Redis Queue + retry |
| **Valet Key** | Acesso temporário a recursos | API Keys com scopes |

### 7.2 Padrão de Handler (FastAPI)

```python
# Todo endpoint PaaS deve:
# 1. Usar dependências de autenticação
# 2. Validar entrada com Pydantic
# 3. Verificar cache
# 4. Executar com circuit breaker
# 5. Registrar consumo
# 6. Retornar resposta padronizada

@router.get("/{tribunal}/{processo}")
async def consultar_processo(
    tribunal: str = Path(...),
    processo: str = Path(...),
    app: App = Depends(get_current_app),  # Auth + quota check
    cache: Cache = Depends(get_cache)
):
    # Validar
    if not validar_numero_unico(processo):
        raise HTTPException(400, detail={
            "code": "NUMERO_PROCESSO_INVALIDO",
            "message": "Formato deve ser NNNNNNN-DD.AAAA.T.RRRR.NNNNN"
        })

    # Cache
    cache_key = f"processo:{app.id}:{tribunal}:{processo}"
    if cached := await cache.get(cache_key):
        return Response(data=cached, cached=True)

    # Executar
    async with circuit_breaker(tribunal):
        resultado = await jud_service.consultar_processo(
            tribunal=tribunal,
            processo=processo
        )

    # Cache + Usage
    await cache.set(cache_key, resultado, ttl=1800)
    await usage.record(app.id, "jud", "processo", credits=1)

    return Response(data=resultado, cached=False)
```

### 7.3 Tratamento de Erros Padronizado

```json
{
  "success": false,
  "error": {
    "code": "TRIBUNAL_INVALIDO",
    "message": "Código de tribunal não reconhecido",
    "details": {
      "tribunal_informado": "TJXX",
      "tribunais_disponiveis": ["TJSP", "TJRJ", "TJMG", "..."],
      "docs_url": "https://docs.jusplatform.com/jud/v1/tribunais"
    }
  },
  "meta": {
    "request_id": "uuid",
    "processing_time_ms": 2,
    "credits_used": 0,
    "credits_remaining": 499
  }
}

Códigos de erro:
├── API_KEY_INVALIDA         → 401
├── API_KEY_EXPIRADA         → 401
├── PLANO_SEM_ACESSO         → 403 (produto não disponível no plano)
├── PARAMETRO_INVALIDO       → 400
├── TRIBUNAL_INVALIDO        → 400
├── NUMERO_PROCESSO_INVALIDO → 400
├── PROCESSO_NAO_ENCONTRADO  → 404
├── RATE_LIMIT_EXCEDIDO      → 429
├── QUOTA_DIARIA_EXCEDIDA    → 429
├── CIRCUIT_BREAKER_ABERTO   → 503
├── FONTE_EXTERNA_INDISP    → 502
├── TIMEOUT                  → 504
└── ERRO_INTERNO             → 500
```

### 7.4 Padrão de Testes (PaaS)

```python
# Testar como se fosse um consumidor real da API:
# 1. Com API Key válida → 200 + dados
# 2. Sem API Key → 401
# 3. Com API Key inválida → 401
# 4. Com quota excedida → 429
# 5. Com parâmetros inválidos → 400
# 6. CORS headers corretos
# 7. Rate limit: N requisições em 1 minuto
# 8. Cache: segunda chamada mais rápida
```

---

## 8. Stack Recomendada

### 8.1 Componentes

| Finalidade | Tecnologia | Versão | Custo |
|-----------|-----------|:------:|:-----:|
| API Gateway | FastAPI + Python | 3.11+ | $0 |
| Cache | Redis | 7 | Variável |
| Filas | RQ / Redis Queue | - | $0 |
| Banco | PostgreSQL + pgvector | 15+ | Variável |
| IA Local | Ollama | latest | $0 |
| Monitoria | Prometheus + Grafana | - | $0 |
| Deploy | Railway / Fly.io | - | Free tier |
| Error Tracking | Sentry | - | Free tier |
| Billing | Stripe / Asaas | - | Taxa |
| Docs | OpenAPI + Stoplight | - | $0 |
| Worker | Celery / RQ Worker | - | $0 |
| Search | Elasticsearch | 8 | Variável |

### 8.2 AI Framework

```
S1 (Ollama, $0):            95% das tarefas
  ├── Sumarização
  ├── Classificação
  ├── Extração de entidades
  ├── Anonimização LGPD
  └── Validação

S3 (DeepSeek Flash, $0.15/M):  5% das tarefas
  ├── Jurimetria complexa
  ├── Geração de documentos
  ├── Análise preditiva
  └── Query rewriting
```

---

## 9. Features e Produtos

### 9.1 Produtos da Plataforma

```
JUS PLATFORM
│
├── 🏛️ JUD — Dados Processuais
│   ├── Consulta de processos
│   ├── Monitoramento de movimentações
│   ├── Busca por parte (CPF/CNPJ/nome)
│   └── Webhooks de eventos
│
├── 🏢 EMP — Dados Corporativos
│   ├── Consulta CNPJ
│   ├── Quadro societário
│   ├── CEP
│   └── Enriquecimento de dados
│
├── 🤖 NLP — Inteligência Jurídica
│   ├── Limpeza e normalização
│   ├── Anonimização LGPD
│   ├── Extração de entidades
│   ├── Classificação de peças
│   ├── Sumarização
│   └── Geração de minutas
│
└── 📊 SCORE — Análise Preditiva
    ├── Risco processual
    ├── Similaridade jurisprudencial
    ├── Jurimetria
    └── Predição de resultados
```

### 9.2 Conexões entre Produtos (Cross-Sell)

```
🏛️ JUD + 🏢 EMP:
  Consultar processo → extrair CNPJ das partes
  → EMP: enriquecer com dados cadastrais
  → Relatório: "Empresa X é réu em 3 processos trabalhistas"

🏛️ JUD + 🤖 NLP:
  Consultar processo → baixar últimas movimentações
  → NLP: sumarizar andamento
  → NLP: classificar risco
  → Relatório: "Processo em fase de execução, valor R$ 50k"

🏛️ JUD + 📊 SCORE:
  Consultar processo → buscar jurisprudência similar
  → SCORE: prever resultado com base em casos análogos
  → Relatório: "83% de chance de êxito baseado em 142 casos similares"

🏛️ JUD + Webhook:
  Monitorar processo → detectar nova movimentação
  → Webhook: notificar sistema do cliente
  → Ação: disparar análise automática
```

### 9.3 Roadmap de Produtos

| Fase | Produto | Prazo | Complexidade |
|:----:|---------|:-----:|:------------:|
| **MVP** | JUD v1 (consulta processo + movimentações) | 4 semanas | Média |
| **MVP** | EMP v1 (CNPJ + CEP via BrasilAPI) | 2 semanas | Baixa |
| **v1.0** | NLP v1 (limpeza + anonimização) | 3 semanas | Média |
| **v1.5** | JUD v2 (busca por CPF/CNPJ) | 3 semanas | Alta |
| **v2.0** | Webhooks + monitoramento | 4 semanas | Alta |
| **v2.5** | NLP v2 (classificação + sumarização) | 6 semanas | Alta |
| **v3.0** | SCORE v1 (jurimetria + predição) | 8 semanas | Muito alta |
| **v3.5** | Developer Hub + SDKs | 4 semanas | Média |
| **v4.0** | NLP v3 (geração de peças) | 8 semanas | Muito alta |

---

## 10. Plano de Monetização

### 10.1 Precificação (Créditos)

```
1 crédito = R$ 0,01 (1 centavo de real)

Plano Free:
  Inclusão: R$ 0/mês
  Créditos: 100/dia (grátis)
  Produtos: JUD (consulta), EMP (CNPJ)
  Limites: 10 req/min, sem webhooks

Plano Pro:
  Inclusão: R$ 49/mês
  Créditos Inclusos: 5.000/mês
  Créditos Adicionais: R$ 0,005/crédito
  Produtos: JUD + EMP + NLP (limpeza + anonimização)
  Limites: 60 req/min, webhooks (5)

Plano Business:
  Inclusão: R$ 199/mês
  Créditos Inclusos: 25.000/mês
  Créditos Adicionais: R$ 0,003/crédito
  Produtos: JUD + EMP + NLP (completo) + SCORE (básico)
  Limites: 300 req/min, webhooks (20)

Plano Enterprise:
  Inclusão: Sob consulta
  Créditos Inclusos: Ilimitados
  Produtos: Tudo
  Limites: Ilimitado, SLA 99.9%, suporte dedicado
```

### 10.2 Tabela de Créditos por Endpoint

| Endpoint | Créditos | Custo estimado |
|----------|:--------:|:--------------:|
| `GET /jud/v1/processos/{numero}` | 1 | R$ 0,01 |
| `GET /jud/v1/busca?documento={cpf}` | 2 | R$ 0,02 |
| `POST /nlp/v1/sumarizar` | 3 | R$ 0,03 |
| `POST /nlp/v1/gerar` | 5 | R$ 0,05 |
| `GET /score/v1/jurimetria/{tribunal}` | 10 | R$ 0,10 |

---

## 11. Referências e Fontes

### 11.1 Documentação Oficial

| Fonte | URL | Descrição |
|-------|-----|-----------|
| CNJ DataJud | `https://www.cnj.jus.br/sistemas/datajud/` | Portal oficial do DataJud |
| CNJ Tabelas Processuais | `https://www.cnj.jus.br/programas-e-acoes/tabela-processuais-unificadas/` | TPU |
| BrasilAPI | `https://brasilapi.com.br/docs` | Documentação OpenAPI |
| Dados Abertos RFB | `https://dados.gov.br/dados/conjuntos-dados/cnpj` | Dump CNPJ |

### 11.2 Repositórios (MIT License ✅)

| Repo | ⭐ | Descrição |
|------|:--:|-----------|
| `BrasilAPI/BrasilAPI` | 10.8K | Agregador APIs públicas BR |
| `felipemaiapolo/legalnlp` | 191 | NLP linguagem jurídica BR |
| `affaan-m/ECC` | 211.9K | Agent Harness OS (padrões agentes) |

### 11.3 Papers

```
Polo et al. "LegalNLP - Natural Language Processing Methods
for the Brazilian Legal Language." ENIAC, 2021. arXiv: 2110.15709

CNJ. "DataJud - Base Nacional de Dados Judiciais."
Resolução CNJ nº 316/2020.
```

### 11.4 Stack Pessoal (Guilherme Crepaldi)

```bash
# Ollama
ollama pull qwen2.5-coder:7b
ollama pull llama3.1:8b
ollama pull gemma3

# Python
pip install legalnlp

# PostgreSQL
# CREATE EXTENSION vector;

# FastAPI + Redis
pip install fastapi uvicorn redis httpx
```

---

> **Nota sobre Clean Room**: Esta spec foi criada através do estudo de
> repositórios MIT (BrasilAPI, LegalNLP), documentação pública (CNJ, DataJud)
> e padrões de engenharia de software. Nenhum código foi copiado.
> Tudo é 100% original e livre para uso comercial.

> **Última atualização**: Julho de 2026
> **Arquitetura**: Platform as a Service (PaaS) — API-first, multi-tenant
> **Repositório**: `guilhermecrepaldi/neo-hermes/specs/`
