---
name: confidential-computing
description: "NVIDIA Confidential Computing — TEE (Trusted Execution Environment) for secure AI inference. Data stays encrypted even during processing. Used by Apple Private Cloud Compute. Potential regulatory requirement under EU AI Act."
category: mlops
tags: [auto-gerado, innovation-scanner, confidential-computing, tee, security, privacy, inference]
---

# Confidential Computing — Skill Auto-Gerado

## Fonte
Extraído das Edições #001, #002, #003 do TOP OF THE HOUR — IA
Cards: "NVIDIA Fornece Confidential Computing para Apple", "Computação Confidencial NVIDIA + Apple Private Cloud"

## O que é
Confidential Computing (computação confidencial) é uma tecnologia baseada em hardware TEE (Trusted Execution Environment) que mantém dados criptografados mesmo durante o processamento. Resolve o dilema da IA na nuvem: você precisa de servidores potentes, mas não quer expor dados sensíveis ao provedor.

## Como implementar no Hermes 2.0
Confidential computing é a viabilizadora técnica para agentes de IA que precisam de poder de nuvem mas não podem expor dados:

1. **Provider routing sensível:** Hermes pode rotear queries com dados sensíveis para provedores que suportam TEE
2. **Verificação de enclave:** Antes de enviar dados, verificar se o provider está rodando em ambiente TEE atestado
3. **Fallback local:** Se TEE não estiver disponível, cair para execução local (Ollama/llama.cpp)

## Comandos
```bash
# Conceito: configurar Hermes para roteamento sensível
hermes config set privacy.mode tee-preferred
hermes config set privacy.fallback local
hermes config set privacy.verified_providers "azure-confidential, gcp-confidential"

# Verificar atestado TEE antes de enviar prompt
hermes privacy attest --provider azure
```

## Referência
https://developer.nvidia.com/confidential-computing
https://www.apple.com/private-cloud-compute/
