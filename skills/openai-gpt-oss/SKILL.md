---
name: openai-gpt-oss
description: "OpenAI gpt-oss-120B e gpt-oss-20B — primeira família de modelos open-weight da OpenAI sob licença Apache 2.0. Inferência local com Ollama/llama.cpp e fine-tuning em hardware consumer."
category: mlops
tags: [auto-gerado, innovation-scanner, openai, open-source, gguf, llama-cpp, ollama]
---

# OpenAI gpt-oss — Skill Auto-Gerado

## Fonte
Extraído da Edição #006 do TOP OF THE HOUR — IA
Card: "OpenAI Lança gpt-oss: Modelos de Peso Aberto 120B/20B Sob Licença Apache 2.0 — Estratégia Open-Source em Resposta à Comunidade"

## O que é
A OpenAI lançou sua primeira família de modelos com pesos abertos sob licença Apache 2.0:
- **gpt-oss-120B**: 117B parâmetros, modelo denso otimizado, 95% do desempenho do GPT-5.5-Codex em coding benchmarks
- **gpt-oss-20B**: 21B parâmetros, roda e faz fine-tuning em hardware consumer (GPU de ~16GB VRAM)

Os modelos permitem fine-tuning, modificação e redistribuição sem restrições. O 20B cabe em uma única GPU consumer para fine-tuning via Unsloth/QLoRA, enquanto o 120B requer um nó H100.

## Como implementar no Hermes 2.0

### 1. Inferência local com Ollama
```bash
# Adicionar modelo ao Ollama
ollama pull hf.co/unsloth/gpt-oss-20b-GGUF:Q4_K_M

# Ou criar Modelfile personalizado
echo 'FROM hf.co/unsloth/gpt-oss-20b-GGUF:Q4_K_M
TEMPLATE "{{ .Prompt }}"
PARAMETER temperature 0.7
PARAMETER top_p 0.9' > Modelfile
ollama create gpt-oss-20b -f Modelfile

# Testar
ollama run gpt-oss-20b "Write a Python function for..."
```

### 2. Inferência com llama.cpp
```bash
# Baixar GGUF
huggingface-cli download unsloth/gpt-oss-20b-GGUF --include "Q4_K_M/*" --local-dir ./models

# Executar
llama-cli -m ./models/gpt-oss-20b-q4_k_m.gguf -p "Seu prompt aqui" -n 512
```

### 3. Fine-tuning com Unsloth (20B em hardware consumer)
```python
from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained(
    "unsloth/gpt-oss-20b",
    max_seq_length=4096,
    load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(model, r=16)
# Treinar com seus dados
```

### 4. Como provider no Hermes (via Ollama)
```yaml
# config.yaml
providers:
  - name: ollama
    models:
      - name: gpt-oss-20b
        max_tokens: 8192
```

## Comandos
```bash
# Download direto do HuggingFace
huggingface-cli download openai/gpt-oss-20b

# Download GGUF quantizado (recomendado para hardware limitado)
huggingface-cli download unsloth/gpt-oss-20b-GGUF --include "Q4_K_M/*"

# Teste rápido com transformers
python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('openai/gpt-oss-20b', device_map='auto')
tokenizer = AutoTokenizer.from_pretrained('openai/gpt-oss-20b')
inputs = tokenizer('Write a Python function', return_tensors='pt').to('cuda')
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0]))
"
```

## Referência
- HuggingFace: https://huggingface.co/openai/gpt-oss-120b
- HuggingFace: https://huggingface.co/openai/gpt-oss-20b
- Blog HuggingFace: https://huggingface.co/blog/welcome-openai-gpt-oss
- Fonte original: OpenAI / HuggingFace
