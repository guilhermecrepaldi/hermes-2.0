# 📚 DIREITO LUX — Dicionário Técnico & Referência Arquitetural

> **Clean Room Spec** — Jul/2026. 100% original.
> Síntese de: DataJud CNJ, LegalNLP, BrasilAPI, Direito Lux MVP, ECC Agent OS.
> Para pesquisa, estudo, entrevistas e implementações futuras.

---

## Índice

1. [Glossário Jurídico-Técnico](#1-glossário-jurídico-técnico)
2. [APIs e Endpoints](#2-apis-e-endpoints)
3. [Modelo de Domínio Unificado](#3-modelo-de-domínio-unificado)
4. [Pipeline de Dados](#4-pipeline-de-dados)
5. [Tribunais Brasileiros — Catálogo Completo](#5-tribunais-brasileiros)
6. [NLP Jurídico Brasileiro](#6-nlp-jurídico-brasileiro)
7. [Boas Práticas e Padrões](#7-boas-práticas-e-padrões)
8. [Stack Recomendada](#8-stack-recomendada)
9. [Features Sugeridas](#9-features-sugeridas)
10. [Referências e Fontes](#10-referências-e-fontes)

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
| **Cache Key** | Hash único que identifica uma consulta. `sha256(f"{tipo}:{tribunal}:{parametros_normalizados}")`. |
| **Sliding Window** | Algoritmo de rate limit que conta requisições em uma janela temporal deslizante. |
| **Backoff Exponencial** | Estratégia de retry: delay aumenta progressivamente (1s, 3s, 5s...). |
| **Stale-while-revalidate** | Estratégia de cache: serve conteúdo velho enquanto atualiza em background. |
| **Anonimização** | Substituição de dados sensíveis por tokens genéricos para cumprir LGPD. |
| **Mascaramento RegEx** | Técnica de substituição de padrões via expressões regulares (CPF → `[documento]`). |
| **Falha Recuperável** | Erro temporário que justifica retry: timeout, 5xx, conexão recusada. |
| **Falha Permanente** | Erro que não deve ser retentado: 400, 401, 403, 404. |
| **SLA** | Service Level Agreement — acordo de nível de serviço (ex: 99.9% uptime). |

---

## 2. APIs e Endpoints

### 2.1 DataJud (CNJ) — Processos Judiciais

Base nacional de processos judiciais, exposta como Elasticsearch.

```
Base URL:      https://datajud.cnj.jus.br
Autenticação:  API Key por CNPJ provider (credenciamento CNJ)
Método:        POST /{indice_tribunal}/_search
Formato:       JSON (Elasticsearch Query DSL)
Cache Vercel:  24h (service-side)
```

**Queries disponíveis:**

| Tipo | Campos ES | Descrição |
|------|-----------|-----------|
| Processo | `numeroProcesso` | Busca por número único do processo |
| Movimentações | `numeroProcesso` + `tipoDocumento: "movimentacao"` | Andamentos processuais |
| Partes | `numeroProcesso` + `tipoDocumento: "parte"` | Partes envolvidas |
| Documentos | `numeroProcesso` + `tipoDocumento: "documento"` | Documentos juntados |
| Lote | `should: [{numeroProcesso: N1}, {numeroProcesso: N2}]` | Múltiplos processos |
| CPF/CNPJ | `numeroDocumentoParte` | Busca por documento da parte |
| Nome | `nomeParte` | Busca por nome da parte |

**Campos ES relevantes do `_source`:**

```
numeroProcesso        → string
classe                → string (código + nome)
assunto               → objeto (árvore de assuntos CNJ)
tribunal              → string (sigla do tribunal)
situacao              → string (situação do processo)
grauOrigem            → string (1 ou 2)
dataAjuizamento       → datetime
dataHoraUltimaAtualizacao → datetime
numeroDocumentoParte  → string (CPF/CNPJ)
nomeParte             → string
tipoParte             → string (PESSOA_FISICA, PESSOA_JURIDICA)
papelParte            → string (AUTOR, REU, TERCEIRO, ADVOGADO...)
dataHora              → datetime (da movimentação)
codigoMovimento       → string (código CNJ)
tipoMovimento         → string
descricaoMovimento    → string
complementoMovimento  → string
sigiloso              → bool
valorCausa            → float
```

### 2.2 BrasilAPI — Dados Públicos Brasileiros

Agregador open-source de APIs governamentais. MIT License.

```
Base URL:      https://brasilapi.com.br
Cache CDN:     Vercel Smart CDN (23 regiões)
Formato:       JSON
Rate Limit:    Uso consciente (sem crawling automático)
```

**Endpoints:**

| Rota | Exemplo | Cache | Descrição |
|------|---------|:-----:|-----------|
| `GET /api/cep/v1/{cep}` | `01310100` | 48h | Endereço por CEP (Correios + ViaCEP + OpenCEP) |
| `GET /api/cep/v2/{cep}` | `01310100` | 48h | Endereço + coordenadas geográficas |
| `GET /api/cnpj/v1/{cnpj}` | `00000000000191` | 24h | Dados completos da empresa |
| `GET /api/banks/v1` | - | 24h | Todos os bancos brasileiros |
| `GET /api/ddd/v1/{ddd}` | `11` | 24h | Cidades e operadoras por DDD |
| `GET /api/feriados/v1/{ano}` | `2026` | Anual | Feriados nacionais |
| `GET /api/fipe/preco/v1/{codigo}` | código FIPE | 24h | Preço de veículos |
| `GET /api/ibge/uf/v1` | - | Anual | Estados brasileiros |
| `GET /api/ibge/municipios/v1/{uf}` | `SP` | Anual | Municípios por UF |
| `GET /api/isbn/v1/{isbn}` | `978...` | 7d | Dados do livro |
| `GET /api/ncm/v1/{ncm}` | código NCM | 24h | Nomenclatura fiscal |
| `GET /api/pix/v1/participants` | - | 24h | Participantes do Pix |
| `GET /api/taxas/v1` | - | 24h | Taxas de juros (Selic, etc.) |
| `GET /api/registrobr/v1/{dominio}` | `dominio.com.br` | 24h | Status de domínio .br |
| `GET /api/cvm/v1/{tipo}` | tipo | 24h | Dados CVM (fundos) |

**Estrutura da resposta CNPJ (minhareceita.org):**

```json
{
  "cnpj": "00000000000191",
  "razao_social": "EMPRESA EXEMPLO LTDA",
  "nome_fantasia": "EMPRESA EXEMPLO",
  "situacao_cadastral": "Ativa",
  "data_situacao_cadastral": "2020-01-01",
  "endereco": {
    "logradouro": "Rua Exemplo",
    "numero": "100",
    "bairro": "Centro",
    "municipio": "São Paulo",
    "uf": "SP",
    "cep": "01000-000"
  },
  "cnae_fiscal": 6202300,
  "cnae_fiscal_descricao": "Desenvolvimento de programas de computador sob encomenda",
  "capital_social": 100000.00,
  "natureza_juridica": "Sociedade Empresária Limitada",
  "qsa": [
    {"nome": "JOÃO SILVA", "qualificacao": "Sócio-Administrador"}
  ],
  "opcao_pelo_simples": true,
  "data_opcao_pelo_simples": "2020-01-01",
  "porte": "ME"
}
```

### 2.3 Fontes Alternativas (Fallbacks)

| Fonte | URL | Uso | Limitação |
|-------|-----|:---:|-----------|
| OpenCEP | `https://opencep.com/v1/{cep}` | CEP gratuito | Menos campos |
| ViaCEP | `https://viacep.com.br/ws/{cep}/json/` | CEP oficial | Latência |
| Minha Receita | `https://minhareceita.org/{cnpj}` | CNPJ gratuito | Pode cair |
| IBGE API | `https://servicodados.ibge.gov.br/api/v1/` | Dados demográficos | Lento |
| BCB Dados Abertos | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados` | Série histórica | Formato CSV |
| HuggingFace LegalNLP | `https://huggingface.co/felipemaiapolo/legalnlp-bert` | BERT jurídico | Modelo ML |

### 2.4 Ollama — IA Local

```
Base URL:      http://localhost:11434
Formato:       JSON (API compatível com OpenAI)
Modelos disp:  qwen2.5-coder:7b, llama3.1:8b, mistral, gemma3
Custo:         $0
LGPD:          ✅ Dados nunca saem da máquina
```

---

## 3. Modelo de Domínio Unificado

### 3.1 Estrutura de Dados

```
┌─────────────────────────────────────────────────────────┐
│                  SOLICITAÇÃO DE CONSULTA                │
├─────────────────────────────────────────────────────────┤
│ id: UUID                                                │
│ tipo: [processo, movimentacoes, partes, documento,      │
│        lote, cnpj, cep, ddd]                           │
│ tenant_id: UUID                                         │
│ usuario_id: UUID                                        │
│ prioridade: [baixa, normal, alta, urgente]               │
├─────────────────────────────────────────────────────────┤
│ PARÂMETROS                                              │
├─────────────────────────────────────────────────────────┤
│ numero_processo: string?   (NNNNNNN-DD.AAAA.T.RRRR.NN) │
│ tribunal: string?          (TJSP, TRF1, TRT2...)       │
│ documento: string?         (CPF ou CNPJ)               │
│ nome_parte: string?                                     │
│ cep: string?               (somente dígitos)            │
│ pagina: int?               (paginação da resposta)      │
│ data_inicio: date?                                      │
│ data_fim: date?                                         │
├─────────────────────────────────────────────────────────┤
│ cache_key: string          (hash sha256 dos params)    │
│ status: [pendente, processando, concluido, falhou,     │
│          em_cache]                                      │
│ max_tentativas: int         (default: 3)               │
└─────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────┐
│                   RESPOSTA DA CONSULTA                  │
├─────────────────────────────────────────────────────────┤
│ id: UUID                                                │
│ solicitacao_id: UUID                                    │
│ status_http: int                                        │
│ duracao_ms: int                                         │
│ veio_do_cache: bool                                     │
├─────────────────────────────────────────────────────────┤
│ DADOS DO PROCESSO (se tipo=processo)                    │
├─────────────────────────────────────────────────────────┤
│ encontrado: bool                                        │
│ numero: string                                          │
│ classe: string                                          │
│ assunto: dict                                           │
│ tribunal: string                                        │
│ situacao: string                                        │
│ instancia: int                                          │
│ data_ajuizamento: date                                  │
│ data_ultima_atualizacao: datetime                       │
│ valor_causa: float?                                     │
│ partes: Parte[]                                         │
│ movimentacoes: Movimentacao[]                           │
├─────────────────────────────────────────────────────────┤
│ DADOS DA EMPRESA (se tipo=cnpj)                        │
├─────────────────────────────────────────────────────────┤
│ razao_social: string                                    │
│ cnpj: string                                            │
│ situacao: string                                        │
│ endereco: Endereco                                      │
│ cnae: string                                            │
│ socios: Socio[]                                         │
│ porte: string                                           │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Entidades Compartilhadas

```typescript
interface Parte {
  tipo: 'PESSOA_FISICA' | 'PESSOA_JURIDICA'
  nome: string
  documento: string          // CPF ou CNPJ (mascarado se LGPD)
  papel: string             // AUTOR, REU, TERCEIRO, ADVOGADO
  advogado?: {
    nome: string
    oab: string             // Número da OAB
    uf: string
  }
}

interface Movimentacao {
  sequencia: number
  data: datetime
  codigo: string            // Código CNJ do movimento
  descricao: string
  complemento?: string
  sigiloso: boolean
  valor?: float
}

interface Tribunal {
  codigo: string            // TJSP, TRF1, TRT2, STF...
  nome: string
  indice_es: string         // api_publica_tjsp
  tipo: TribunalTipo
  instancia: 1 | 2
  regiao: string
  ativo: boolean
}

type TribunalTipo =
  | 'supremo' | 'superior' | 'federal'
  | 'estadual' | 'trabalho' | 'eleitoral' | 'militar'

interface Endereco {
  logradouro: string
  numero: string
  complemento?: string
  bairro: string
  cidade: string
  uf: string
  cep: string
}

interface Socio {
  nome: string
  qualificacao: string
  percentual?: float
}
```

---

## 4. Pipeline de Dados

### 4.1 Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────────────────────┐
│                          API GATEWAY                               │
│              FastAPI + Rate Limit + Auth JWT                       │
│              CORS + Cache (s-maxage) + Logger                      │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     ORQUESTRADOR DE CONSULTAS                      │
│                                                                     │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Cache   │  │  Circuit     │  │  Rate        │  │  Tribunal  │ │
│  │  (Redis) │→ │  Breaker     │→ │  Limiter     │→ │  Router    │ │
│  └──────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│   ├ hash(params)  ├ por tribunal  ├ sliding window  ├ código→índice│
│   ├ TTL por tipo  ├ 5 falhas→30s  ├ por tenant      ├ + fallback   │
│   └ namespace     └ half-open     └ por plano       └ alternativo  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CLIENTE DE CONSULTA (com retry)                   │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Query       │  │  HTTP        │  │  Response                │  │
│  │  Builder     │→ │  Client      │→ │  Parser                  │  │
│  │              │  │              │  │                          │  │
│  │ monta JSON   │  │ POST _search │  │ ES hits → domain objects │  │
│  │ ES Query DSL │  │ timeout 30s  │  │ extração de campos       │  │
│  │              │  │ retry 3x     │  │ normalização de datas    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                     │
│  FONTES: DataJud (ES), BrasilAPI, minhareceita.org                  │
│  FALLBACK: DataJud → scraper tribunal, OpenCEP → ViaCEP            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PROCESSADOR DE SAÍDA                          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Formatador  │  │  Cache       │  │  Métricas                │  │
│  │  JSON        │→ │  Store       │→ │  Prometheus              │  │
│  │              │  │              │  │                          │  │
│  │ schema único │  │ redis.setex  │  │ duração, hits, erros     │  │
│  │ padronizado  │  │ com TTL      │  │ circuit breaker state    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CAMADA DE INTELIGÊNCIA (opcional)                │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Anonimizador    │  │  Ollama      │  │  LLM Cloud           │ │
│  │  LGPD            │→ │  Local       │→ │  (opcional)          │ │
│  │                  │  │              │  │                      │ │
│  │ mascara CPF/OAB  │  │ sumarização  │  │ jurimetria complexa  │ │
│  │ remove nomes     │  │ classificação│  │ geração documentos   │ │
│  └──────────────────┘  └──────────────┘  └──────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
                    RESPOSTA FINAL (JSON)
```

### 4.2 Política de Retry

```
Tentativa 0: delay 0s
Tentativa 1: delay 1s
Tentativa 2: delay 3s
Tentativa 3: delay 5s (máximo)

✅ RETENTAR:
  timeout de conexão, timeout de leitura
  HTTP 500, 502, 503, 504
  erro de DNS, conexão recusada

❌ NÃO RETENTAR:
  HTTP 400 (Bad Request)
  HTTP 401 (Unauthorized)
  HTTP 403 (Forbidden)
  HTTP 404 (Not Found)
  HTTP 429 (Too Many Requests)
```

### 4.3 Circuit Breaker (por tribunal)

```
FECHADO ──5 falhas consecutivas──▶ ABERTO
  ▲                                   │
  │                                   │
  └──3 sucessos seguidos── MEIO-ABERTO◀──30 segundos
```

### 4.4 Cache Strategy

```
Cache Key = sha256(f"{tenant_id}:{tipo_consulta}:{tribunal}:{parametros_normalizados}")

Namespace: cada tenant (escritório) tem cache isolado

TTL por tipo:
  Processo:     1h (dados estáveis)
  Movimentação: 30min (muda com frequência)
  Partes:       2h (raramente muda)
  CNPJ:         24h (dados cadastrais)
  CEP:          48h (muito estável)

Invalidação manual:
  Por tribunal, processo, ou tenant
```

### 4.5 Rate Limiting (por plano)

```
Básico:      10 req/min,   500 req/dia
Profissional: 60 req/min,  3000 req/dia
Enterprise:  300 req/min, 50000 req/dia

Implementação: sliding window no Redis
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

| Código | Nome | Índice ES | Abrangência |
|--------|------|-----------|-------------|
| TRF1 | TRF 1ª Região | `api_publica_trf1` | AC, AM, AP, BA, DF, GO, MA, MG, MT, PA, PI, RO, RR, TO |
| TRF2 | TRF 2ª Região | `api_publica_trf2` | ES, RJ |
| TRF3 | TRF 3ª Região | `api_publica_trf3` | MS, SP |
| TRF4 | TRF 4ª Região | `api_publica_trf4` | PR, RS, SC |
| TRF5 | TRF 5ª Região | `api_publica_trf5` | AL, CE, PB, PE, RN, SE |
| TRF6 | TRF 6ª Região | `api_publica_trf6` | MG |

**Estaduais (27):**

| Código | UF | Índice ES |
|--------|:--:|-----------|
| TJAC | AC | `api_publica_tjac` |
| TJAL | AL | `api_publica_tjal` |
| TJAP | AP | `api_publica_tjap` |
| TJAM | AM | `api_publica_tjam` |
| TJBA | BA | `api_publica_tjba` |
| TJCE | CE | `api_publica_tjce` |
| TJDFT | DF | `api_publica_tjdft` |
| TJES | ES | `api_publica_tjes` |
| TJGO | GO | `api_publica_tjgo` |
| TJMA | MA | `api_publica_tjma` |
| TJMT | MT | `api_publica_tjmt` |
| TJMS | MS | `api_publica_tjms` |
| TJMG | MG | `api_publica_tjmg` |
| TJPA | PA | `api_publica_tjpa` |
| TJPB | PB | `api_publica_tjpb` |
| TJPR | PR | `api_publica_tjpr` |
| TJPE | PE | `api_publica_tjpe` |
| TJPI | PI | `api_publica_tjpi` |
| TJRJ | RJ | `api_publica_tjrj` |
| TJRN | RN | `api_publica_tjrn` |
| TJRS | RS | `api_publica_tjrs` |
| TJRO | RO | `api_publica_tjro` |
| TJRR | RR | `api_publica_tjrr` |
| TJSC | SC | `api_publica_tjsc` |
| **TJSP** | **SP** | **`api_publica_tjsp`** ← maior tribunal do país |
| TJSE | SE | `api_publica_tjse` |
| TJTO | TO | `api_publica_tjto` |

**Trabalhistas (24):** TRT01 a TRT24 → `api_publica_trt{NN}`

**Eleitorais (27):** TREAM a TRETO → `api_publica_tre{uf}`

**Militares (3):** TJMSP, TJMMG, TJMRS → `api_publica_{sigla}`

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
  │   └── lowercasing (opcional, exceto BERT)
  │
  ▼ Mascaramento RegEx
  │   ├── [url]:    http\S+ | www\S+
  │   ├── [email]:  [^\s]+@[^\s]+
  │   ├── [oab]:    OAB\s?[:-]?\d+\s?/?\s?[A-Z]+
  │   ├── [data]:   \d{2}\s?\/\s?\d{2}\s?\/\s?\d{4}
  │   ├── [processo]: \d{15,} (15+ dígitos)
  │   ├── [valor]:  R\s?\$\s?\d+[.,]?\d*
  │   └── [numero]: \d+
  │
  ▼ Pós-processamento
  │   ├── siglas sem pontos (C.P.F → CPF)
  │   ├── plurais/gênero ((s), (a), (o))
  │   ├── hífens junção (arquivem - se → arquivem-se)
  │   └── espaços extras
  │
  ▼ TEXTO LIMPO + DICT com entidades extraídas
```

### 6.2 Aplicações de NLP no Contexto Jurídico

| Aplicação | Input | Output | Modelo |
|-----------|-------|--------|--------|
| Classificação de peças | Texto de petição | Tipo (inicial, contestação, sentença...) | BERTikal / Ollama |
| Extração de entidades | Texto jurídico | Leis, valores, prazos, OAB | RegEx + Ollama |
| Similaridade jurisprudencial | 2 ementas | Score de similaridade | Word2Vec / embeddings |
| Busca semântica | Query em linguagem natural | Processos similares | pgvector + embeddings |
| Sumarização | Decisão judicial longa | Resumo em 3 parágrafos | Ollama (local) |
| Anonimização LGPD | Texto com dados pessoais | Texto anonimizado | RegEx + Ollama |
| Geração de peças | Template + variáveis | Petição/parecer completo | LLM Cloud |
| Análise de risco | Processo + jurisprudência | Probabilidade de êxito | LLM Cloud |

### 6.3 Modelos Pré-Treinados

| Modelo | Tipo | Tamanho | Acesso |
|--------|------|:-------:|--------|
| **BERTikal** | BERT-base (português jurídico) | 110M params | HuggingFace: `felipemaiapolo/legalnlp-bert` |
| **Word2Vec CBOW** | Embeddings (100d) | ~200MB | Figshare + `get_premodel('wodc')` |
| **Word2Vec Skip-Gram** | Embeddings (100d) | ~200MB | Figshare + `get_premodel('wodc')` |
| **FastText CBOW** | Embeddings sub-word (100d) | ~200MB | Figshare + `get_premodel('fasttext')` |
| **FastText SG** | Embeddings sub-word (100d) | ~200MB | Figshare + `get_premodel('fasttext')` |
| **Phraser** | Detecção de bigramas | ~5MB | Figshare + `get_premodel('phraser')` |
| **NeuralMind BERT** | BERT-base português (não jurídico) | 110M params | NeuralMind AWS S3 |
| **qwen2.5-coder:7b** | LLM generalista | 4.7GB | Ollama local |

### 6.4 Instalação (LegalNLP)

```bash
pip install legalnlp

# Uso básico
from legalnlp.clean_functions import clean, clean_bert

texto = "O autor, CPF 000.000.000-00, propõe ação..."
texto_limpo = clean(texto, lower=True, return_masked=True)
# → {'txt': 'o autor [documento] propoe acao ...',
#    'oab': [], 'data': [], 'processo': [],
#    'valor': [], 'numero': ['000', '000', '000', '00']}
```

---

## 7. Boas Práticas e Padrões

### 7.1 Padrões de Projeto

| Padrão | Quando usar | Exemplo |
|--------|-------------|---------|
| **Proxy** | Quando precisa de uma fachada pra API externa | BrasilAPI → minhareceita.org |
| **Proxy com Fallback** | Quando há múltiplas fontes concorrentes | CEP: OpenCEP → cep-promise |
| **Circuit Breaker** | Serviço externo instável | DataJud por tribunal |
| **Retry com Backoff** | Falhas transitórias esperadas | Timeout de conexão |
| **Cache-Aside** | Dados que mudam pouco | CNPJ, CEP, dados de processo |
| **Rate Limiter** | Proteger backend de abuso | Plano Básico: 10 req/min |
| **Strangler Fig** | Migração gradual de API legada | V1 → V2 endpoints |
| **Ambassador** | Sidecar para tratar comunicação externa | Middleware de cache + retry |

### 7.2 Padrão de Handler (FastAPI)

```python
# Estrutura padrão para cada endpoint
# 1. Router com prefixo
# 2. Validar entrada (Pydantic)
# 3. Verificar cache
# 4. Executar serviço
# 5. Tratar erros específicos
# 6. Retornar resposta padronizada
# 7. Atualizar cache

@router.get("/{tribunal}/{processo}")
async def consultar_processo(
    tribunal: str,
    processo: str,
    request: Request
):
    # Validar formato do processo
    if not validar_numero_unico(processo):
        raise BadRequest("Formato de processo inválido")

    # Verificar cache
    cache_key = gerar_cache_key("processo", tribunal, processo)
    if cached := await cache.get(cache_key):
        return cached

    # Executar com proteções
    async with circuit_breaker(tribunal):
        resultado = await datajud_service.consultar_processo(
            tribunal=tribunal,
            processo=processo
        )

    # Atualizar cache
    await cache.set(cache_key, resultado, ttl=3600)

    return resultado
```

### 7.3 Tratamento de Erros Padronizado

```json
{
  "erro": {
    "codigo": "TRIBUNAL_INVALIDO",
    "mensagem": "Código de tribunal não reconhecido",
    "detalhes": {
      "tribunal_informado": "TJXX",
      "tribunais_disponiveis": ["TJSP", "TJRJ", "TJMG", "..."]
    },
    "solicitacao_id": "uuid"
  }
}

Códigos de erro comuns:
├── PARAMETRO_INVALIDO    → 400
├── TRIBUNAL_INVALIDO     → 400
├── PROCESSO_NAO_ENCONTRADO → 404
├── RATE_LIMIT_EXCEDIDO   → 429
├── CIRCUIT_BREAKER_ABERTO → 503
├── FONTE_EXTERNA_INDISPONIVEL → 502
└── TIMEOUT              → 504
```

### 7.4 Padrão de Testes

```python
# Todo endpoint deve testar:
# 1. Sucesso com parâmetros válidos → 200 + JSON correto
# 2. Parâmetros inválidos → 400 + mensagem de erro
# 3. Dado não encontrado → 404
# 4. CORS funcionando → headers corretos
# 5. Cache funcionando → segunda chamada mais rápida
```

---

## 8. Stack Recomendada

### 8.1 Tecnologias

| Finalidade | Tecnologia | Versão | Custo |
|-----------|-----------|:------:|:-----:|
| API | FastAPI + Python | 3.11+ | $0 |
| Cache | Redis | 7 | Variável |
| Filas | RQ / Celery | - | $0 |
| Vetores | pgvector (PostgreSQL) | 15+ | $0 |
| IA Local | Ollama | última | $0 |
| Monitoria | Prometheus + Grafana | - | $0 |
| Deploy | Vercel / Railway | - | Free tier |
| Search | Elasticsearch | 8 | Variável |
| Observabilidade | Sentry | - | Free tier |

### 8.2 Framework de IA (Shellz / Hermes)

```
S1 (Ollama, $0):       95% das tarefas
  - sumarização, classificação, extração
  - anonimização LGPD
  - validação de dados

S3 (DeepSeek, $0.15/M): 5% das tarefas
  - jurimetria complexa
  - geração de documentos
  - análise preditiva
```

---

## 9. Features Sugeridas

### 9.1 Features Imediatas (NowPro +)

| Feature | Descrição | Dados Necessários | API |
|---------|-----------|-------------------|:---:|
| **Busca Unificada** | CPF/CNPJ → dados empresa + processos + score | BrasilAPI + DataJud | 📡 |
| **Alertas de Movimentação** | Notificação quando houver nova movimentação | DataJud + Webhook | 📡 |
| **Anonimizador Automático** | Mascarar dados sensíveis em documentos jurídicos | LegalNLP | 🤖 |
| **Classificador de Peças** | Detectar tipo de peça processual automaticamente | LegalNLP + Ollama | 🤖 |
| **Calculadora de Prazos** | Dias úteis, suspensão, feriados | BrasilAPI (feriados) | 📡 |

### 9.2 Features Estratégicas (6 meses)

| Feature | Descrição | APIs Necessárias |
|---------|-----------|:----------------:|
| **Jurimetria Automática** | Probabilidade de êxito por tribunal/classe/assunto | DataJud + Ollama |
| **Relatório de Risco** | Score de risco processual completo | DataJud + BrasilAPI + Ollama |
| **Busca Semântica** | Encontrar processos similares por embedding | pgvector + embeddings |
| **Geração de Peças** | Minuta automática de petições | Ollama + templates |
| **Dashboard Executivo** | KPIs do escritório em tempo real | DataJud + métricas |
| **MCP Bot** | Interface conversacional WhatsApp/Telegram | MCP + Notification |

### 9.3 Conexões entre Domínios

```
CPF da parte
  → BrasilAPI: dados cadastrais (nome, situação)
  → DataJud: processos como autor/réu
  → LegalNLP: anonimizar
  → Ollama: sumarizar perfil processual
  → Relatório: "score jurídico" da pessoa

CNPJ da empresa
  → BrasilAPI: razão social, sócios, CNAE, porte
  → DataJud: processos trabalhistas, fiscais, cíveis
  → Ollama: classificar risco trabalhista
  → Relatório: Due diligence resumida

Número de processo
  → DataJud: andamentos, movimentações, valor, partes
  → LegalNLP: extrair prazos, OAB, valores
  → Ollama: prever próximas movimentações
  → Alerta automático: "prazo de 15 dias para contestação"
```

---

## 10. Referências e Fontes

### 10.1 Documentação Oficial

| Fonte | URL | Descrição |
|-------|-----|-----------|
| CNJ DataJud | `https://www.cnj.jus.br/sistemas/datajud/` | Portal oficial do DataJud |
| CNJ Tabelas Processuais | `https://www.cnj.jus.br/programas-e-acoes/tabela-processuais-unificadas/` | TPU (classes, assuntos, movimentos) |
| BrasilAPI | `https://brasilapi.com.br/docs` | Documentação OpenAPI |
| Dados Abertos RFB | `https://dados.gov.br/dados/conjuntos-dados/cnpj` | Dump CNPJ Receita Federal |

### 10.2 Repositórios (MIT License ✅)

| Repo | ⭐ | Descrição |
|------|:--:|-----------|
| `BrasilAPI/BrasilAPI` | 10.8K | Agregador APIs públicas BR |
| `felipemaiapolo/legalnlp` | 191 | NLP para linguagem jurídica BR |
| `affaan-m/ECC` | 211.9K | Agent Harness OS (padrões de hooks e agentes) |

### 10.3 Artigos e Pesquisas

```
Polo et al. "LegalNLP - Natural Language Processing Methods
for the Brazilian Legal Language." ENIAC, 2021.
arXiv: 2110.15709

CNJ. "DataJud - Base Nacional de Dados Judiciais."
Resolução CNJ nº 316/2020.

ABJ (Associação Brasileira de Jurimetria).
Pesquisas e dados abertos sobre o Poder Judiciário.
```

### 10.4 Instalações Úteis

```bash
# LegalNLP
pip install legalnlp

# Ollama (modelos jurídicos)
ollama pull qwen2.5-coder:7b    # Geral
ollama pull llama3.1:8b          # Alternativa
ollama pull gemma3               # Google

# pgvector (PostgreSQL)
# CREATE EXTENSION vector;
```

---

> **Nota sobre Clean Room**: Esta spec foi criada através do estudo de
> repositórios MIT (BrasilAPI, LegalNLP), documentação pública (CNJ, DataJud)
> e padrões de engenharia de software. Nenhum código foi copiado.
> Tudo é 100% original e livre para uso comercial.

> **Última atualização**: Julho de 2026
> **Autor**: Neo Hermes (guilhermecrepaldi)
> **Repositório**: `guilhermecrepaldi/neo-hermes/specs/`
