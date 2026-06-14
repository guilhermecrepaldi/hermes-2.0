---
name: glm-5-2
description: "GLM 5.2 — modelo MoE 130B (12B ativos) da Zhipu AI, open-source (MIT), 1M tokens de contexto, foco em coding e raciocínio. Competidor direto de Qwen 3.7 e DeepSeek V4."
category: mlops
tags: [auto-gerado, innovation-scanner, hermes-2.0, model-provider, zhipu-ai, chinese-llm, moe]
---

# GLM 5.2 — Modelo de Fronteira Chinês Open-Source (MIT)

## Fonte
Extraído da Edição #005 do TOP OF THE HOUR — IA
Card: "GLM 5.2 é Lançado com Pesos Abertos Previstos para a Próxima Semana — Novo Challenger Chinês"

## O que é
O GLM 5.2 é o modelo de fronteira mais recente da Zhipu AI (Beijing, China), uma das "4 tigres" da IA chinesa. Com arquitetura MoE (Mixture of Experts) de 130B parâmetros (12B ativos por token), oferece 1 milhão de tokens de contexto e pesos abertos sob licença MIT. A versão GLM-5.2-Coder compete diretamente com Qwen3-Coder e DeepSeek-Coder-V4 em benchmarks de programação.

## Como implementar no Hermes 2.0

### Via HuggingFace (local)
```bash
# Baixar o modelo
huggingface-cli download THUDM/glm-5-2 --local-dir ./models/glm-5-2

# Executar com llama.cpp (GGUF)
# Ou usar diretamente via transformers
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('THUDM/glm-5-2', device_map='auto')
tokenizer = AutoTokenizer.from_pretrained('THUDM/glm-5-2')
"
```

### Via API (Zhipu)
```bash
# API key da Zhipu
export ZHIPU_API_KEY="sua-chave"
curl https://open.bigmodel.cn/api/llm/v1/glm-5-2 \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -d '{"prompt": "write a python fibonacci function", "max_tokens": 1024}'
```

### Como provider no Hermes
Adicione no `config.yaml`:
```yaml
providers:
  glm:
    type: openai-compatible
    base_url: https://open.bigmodel.cn/api/llm/v1
    api_key: ${ZHIPU_API_KEY}
    models:
      - glm-5-2
      - glm-5-2-coder
```

## Comandos
```bash
# Download dos pesos
huggingface-cli download THUDM/glm-5-2

# Chat via API
curl -X POST https://open.bigmodel.cn/api/llm/v1/glm-5-2 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"max_tokens":512}'
```

## Referência
- HuggingFace: https://huggingface.co/THUDM/glm-5-2 (pesos MIT)
- Blog: https://codersera.com/blog/glm-5-2-release-1m-context-coding-2026/
- Plataforma: https://open.bigmodel.cn
- GLM Coding Plan: https://www.zhipu.ai/glm-coding-plan
