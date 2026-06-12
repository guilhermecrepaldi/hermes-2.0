---
name: open-llm-vtuber
description: "Open-source voice interaction platform for any LLM — speech-to-speech with interruption support, Live2D avatar, and emotion-aware TTS. Full local execution."
category: autonomous-ai-agents
tags: [voice, tts, asr, avatar, llm-interface, auto-gerado, innovation-scanner]
---

# Open-LLM-VTuber — Voice Interaction Platform for Any LLM

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA
Card: "Open-LLM-VTuber: Fale com Qualquer LLM com Voz, Interrupção e Avatar 3D em Tempo Real"

## O que é
Open-LLM-VTuber é uma plataforma open-source que permite interação por voz com qualquer LLM. Suporta interrupção de fala (barge-in), avatar Live2D com expressões faciais sincronizadas e execução local completa. Destaque no GitHub Trending pelo pipeline completo de voz + IA.

### Pipeline
```
Microfone → ASR (reconhecimento de fala) → LLM → TTS (síntese de voz) → Avatar 3D + Alto-falante
                ↕ (interrupção permitida a qualquer momento)
```

## Como implementar no Hermes 2.0
Esta skill documenta a arquitetura para referência em projetos de interface de voz com IA.

### Componentes principais
- **ASR**: reconhecimento de fala em tempo real (whisper, faster-whisper)
- **LLM Router**: suporta qualquer LLM (OpenAI, Anthropic, Ollama local)
- **TTS Engine**: múltiplas vozes (VibeVoice, Edge TTS, OpenAI TTS)
- **Avatar Engine**: renderização Live2D com expressões faciais
- **Interruption Handler**: permite corte de fala durante resposta

### Arquitetura para Hermes
```python
# Exemplo conceitual de pipeline de voz
from open_llm_vtuber import VoicePipeline, ASRConfig, TTSConfig

pipeline = VoicePipeline(
    asr=ASRConfig(model="whisper-large-v3", language="pt"),
    tts=TTSConfig(provider="edge", voice="pt-BR-AntonioNeural"),
    llm_endpoint="http://localhost:11434/v1/chat/completions",
    interrupt_enabled=True
)

response = pipeline.chat_with_voice("Olá, qual a última notícia?")
# A conversa flui naturalmente com áudio e avatar
```

## Comandos
```bash
# Clonar e executar
git clone https://github.com/Open-LLM-VTuber/Open-LLM-VTuber
cd Open-LLM-VTuber
pip install -r requirements.txt
python app.py
```

## Referência
- Repositório: https://github.com/Open-LLM-VTuber/Open-LLM-VTuber
- Fonte original: GitHub Trending
