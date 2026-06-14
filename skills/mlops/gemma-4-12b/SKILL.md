---
name: gemma-4-12b
description: "Google DeepMind Gemma 4 12B — modelo multimodal encoder-free que integra texto, imagem, áudio e vídeo nativamente. Aberto, gratuito para uso comercial, roda em 16GB VRAM."
category: mlops
tags: [auto-gerado, innovation-scanner, hermes-2.0, model-provider, google-deepmind, multimodal, open-model]
---

# Gemma 4 12B — Modelo Multimodal Encoder-Free

## Fonte
Extraído da Edição #004 do TOP OF THE HOUR — IA
Card: "Google DeepMind Lança Gemma 4 12B: Modelo Multimodal Encoder-Free"

## O que é
O Gemma 4 12B é o primeiro modelo multimodal de médio porte da Google DeepMind que integra texto, imagem, áudio e vídeo sem encoder separado — unificando a arquitetura. Diferente de soluções tipo CLIP + LLM, o Gemma 4 processa múltiplos modalities nativamente em uma única passagem. Roda em hardware modesto (16GB VRAM), é aberto e gratuito para uso comercial.

## Como implementar no Hermes 2.0

### Via HuggingFace
```bash
# Baixar o modelo
huggingface-cli download google/gemma-4-12B --local-dir ./models/gemma-4-12b

# Testar inferência
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('google/gemma-4-12B', device_map='auto')
tokenizer = AutoTokenizer.from_pretrained('google/gemma-4-12B')

# Processar imagem + texto
messages = [
    {'role': 'user', 'content': [
        {'type': 'image', 'url': 'https://example.com/photo.jpg'},
        {'type': 'text', 'text': 'Descreva esta imagem'}
    ]}
]
inputs = tokenizer.apply_chat_template(messages, return_tensors='pt').to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512)
print(tokenizer.decode(outputs[0]))
"
```

### Como API local (recomendado para Hermes)
```bash
# Opção 1: Usar o servidor de inferência do HuggingFace
python3 -m transformers.server --model google/gemma-4-12B --port 8080

# Opção 2: Usar llama.cpp versão multimodal (suporte experimental)
# Opção 3: Usar vLLM com suporte multimodal (se disponível)
```

### Como provider no Hermes (via API local)
```yaml
providers:
  gemma4:
    type: openai-compatible
    base_url: http://localhost:8080/v1
    api_key: none
    models:
      - gemma-4-12b
```

## Casos de Uso no Hermes
- **Visão computacional + linguagem local**: descrever imagens, OCR contextual, VQA sem depender de API externa
- **Análise de screenshots**: interpretar capturas de tela de ferramentas e sistemas
- **Processamento de documentos**: extrair informações de PDFs/imagens escaneadas localmente
- **Agente multimodal**: combinar entrada visual + textual em loops de agente autônomo

## Comandos
```bash
# Download
huggingface-cli download google/gemma-4-12B

# Inferência básica
python3 -c "
from transformers import pipeline
pipe = pipeline('text-generation', model='google/gemma-4-12B')
print(pipe('Explain neural networks')[0]['generated_text'])
"
```

## Referência
- HuggingFace: https://huggingface.co/google/gemma-4-12B
- Google Developers Blog: https://developers.googleblog.com/gemma-4-12b-the-developer-guide/
- Google Keyword: https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemma-4-12B/
