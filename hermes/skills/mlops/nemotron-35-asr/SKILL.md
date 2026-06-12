---
name: nemotron-35-asr
description: "NVIDIA Nemotron 3.5 ASR — fine-tunable open-source speech recognition for multilingual, domain-specific voice applications. Adapt to any language or accent."
category: mlops
tags: [asr, speech-recognition, nvidia, fine-tuning, whisper-alternative, auto-gerado, innovation-scanner]
---

# Nemotron 3.5 ASR — Fine-Tuning para Reconhecimento de Fala Multilíngue

## Fonte
Extraído da Edição #003 do TOP OF THE HOUR — IA
Card: "NVIDIA Nemotron 3.5 ASR: Fine-Tuning para Reconhecimento de Fala Multilíngue"

## O que é
NVIDIA Nemotron 3.5 ASR é um modelo open-source de reconhecimento automático de fala que pode ser fine-tunado para idiomas, domínios ou sotaques específicos. Permite adaptação com apenas ~10 horas de áudio transcrito e execução local no dispositivo.

### Diferenciais
- **Fine-tuning acessível**: ~10 horas de áudio para adaptação
- **Multilíngue**: suporte nativo a múltiplos idiomas
- **Execução local**: privacidade total, sem dependência de nuvem
- **Domínios específicos**: telemedicina, call centers, idiomas com poucos recursos

## Como implementar no Hermes 2.0
Pode substituir ou complementar o ASR atual no pipeline de voz do Hermes.

### Fine-tuning básico
```python
from transformers import AutoModelForCTC, AutoProcessor
import torch

model = AutoModelForCTC.from_pretrained("nvidia/nemotron-3.5-asr")
processor = AutoProcessor.from_pretrained("nvidia/nemotron-3.5-asr")

# Adaptar para domínio específico
# 1. Prepare dataset de áudio transcrito
# 2. Use o script oficial de fine-tuning
# 3. Avalie em dados de validação
```

### Uso para inferência
```bash
# Transcrever áudio localmente
python transcribe.py --model nvidia/nemotron-3.5-asr --audio speech.wav

# Fine-tuning para português
python finetune_asr.py \
  --model nvidia/nemotron-3.5-asr \
  --dataset seu-dataset-pt \
  --output-dir ./nemotron-pt
```

## Comandos
```bash
# Baixar modelo
huggingface-cli download nvidia/nemotron-3.5-asr

# Testar com áudio
python -c "
from transformers import pipeline
asr = pipeline('automatic-speech-recognition', model='nvidia/nemotron-3.5-asr')
result = asr('audio.wav')
print(result['text'])
"
```

## Referência
- Guia oficial: https://huggingface.co/blog/nvidia/fine-tuning-nemotron-35-asr
- Fonte original: HuggingFace / NVIDIA Blog
