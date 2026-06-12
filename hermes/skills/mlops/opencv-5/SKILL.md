---
name: opencv-5
description: "OpenCV 5 — the biggest leap in years for computer vision with native CUDA, accelerated video pipelines, and redesigned API"
category: mlops
tags: [auto-gerado, innovation-scanner, vision, cuda]
---

# OpenCV 5 — Skill Auto-Gerado

## Fonte
Extraído da Edição #001 do TOP OF THE HOUR — IA
Card: "OpenCV 5 Chegou: O Maior Salto em Anos para Visão Computacional com CUDA Nativo"

## O que é
OpenCV 5 é a atualização mais significativa da biblioteca de visão computacional em mais de uma década. Traz suporte nativo a CUDA (aceleração de 10-50× em pipelines de visão sem escrever um único kernel), novos algoritmos de deep learning, pipeline de vídeo acelerado por hardware e API redesenhada.

## Como implementar no Hermes 2.0
OpenCV 5 pode ser usado como dependência para skills de visão computacional dentro do Hermes. Instalação via pip:

```bash
pip install opencv-python==5.*
```

Para aceleração CUDA, instale o pacote com suporte CUDA:
```bash
pip install opencv-contrib-python==5.*
```

## Comandos

```python
import cv2

# Verificar versão
print(cv2.__version__)  # 5.x.x

# CUDA está disponível?
print(cv2.cuda.getCudaEnabledDeviceCount())

# Pipeline acelerado por GPU
img = cv2.imread('input.jpg')
gpu_img = cv2.cuda_GpuMat()
gpu_img.upload(img)
gpu_gray = cv2.cuda.cvtColor(gpu_img, cv2.COLOR_BGR2GRAY)
result = gpu_gray.download()
```

## Referência
- https://opencv.org/
- https://github.com/opencv/opencv
- Fonte original: Hacker News (810 pontos)
