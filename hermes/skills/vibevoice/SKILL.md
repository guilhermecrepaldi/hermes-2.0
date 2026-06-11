---
name: vibevoice
description: "Microsoft open-source TTS system rivaling ElevenLabs — local voice synthesis with emotion, cloning, and multi-language support"
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, tts, voice, speech, microsoft]
---

# VibeVoice — Microsoft Open-Source TTS

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA
Card: "microsoft/VibeVoice: Voz Sintética de Fronteira em Código Aberto — Concorrente do ElevenLabs?" (app-002-05)

## O que é
VibeVoice é uma plataforma de voz sintética open-source lançada pela Microsoft que rivaliza com ElevenLabs e OpenAI TTS. Oferece:
- Síntese de voz natural em múltiplos idiomas
- Clonagem de voz (voice cloning)
- Suporte a emoções e entonação
- Execução **local** (dados nunca saem da máquina)
- Controle total sobre o modelo

## Como implementar no Hermes 2.0

### Instalação
```bash
git clone https://github.com/microsoft/VibeVoice.git
cd VibeVoice
pip install -r requirements.txt
pip install -e .
```

### Uso básico
```python
from vibevoice import VibeVoice

tts = VibeVoice(model_name="vibevoice-base")
tts.speak("Olá, esta é uma voz sintética natural.", 
          voice="pt-BR",
          emotion="friendly",
          output_path="output.wav")
```

### Integração como provider TTS no Hermes
No arquivo de configuração do Hermes, adicione VibeVoice como provider TTS:
```yaml
tts:
  provider: vibevoice
  vibevoice:
    model: vibevoice-base
    voice: pt-BR
    emotion: friendly
```

## Comandos
```bash
# Clonar repositório
git clone https://github.com/microsoft/VibeVoice.git

# Executar playground
python vibevoice/playground.py

# Síntese via CLI
python -m vibevoice.cli --text "Hello world" --voice en-US --output out.wav
```

## Vantagens sobre Edge TTS (atual provider padrão)
- ✅ Execução 100% local — sem dependência de API externa
- ✅ Clonagem de voz disponível
- ✅ Controle de emoções e entonação
- ✅ Modelo open-source — auditável e customizável
- ⚠️ Pode exigir GPU para desempenho ideal

## Referência
https://github.com/microsoft/VibeVoice
