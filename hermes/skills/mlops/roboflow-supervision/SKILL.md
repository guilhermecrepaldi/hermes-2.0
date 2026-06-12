---
name: roboflow-supervision
description: "roboflow/supervision — reusable computer vision tools library for detection, segmentation, tracking, annotation, and visualization. Works with any model (YOLO, SAM, DETR)."
category: mlops
tags: [auto-gerado, innovation-scanner, computer-vision, annotation, detection]
---

# roboflow/supervision — Skill Auto-Gerado

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA (app-002-06)
Card: "roboflow/supervision: Ferramentas de Visão Computacional Reutilizáveis para Qualquer Projeto"

## O que é
roboflow/supervision é uma biblioteca Python open-source que oferece ferramentas reutilizáveis de visão computacional — detecção de objetos, segmentação, rastreamento, anotação de datasets e visualização — funcionando com qualquer modelo (YOLO, SAM, DETR, etc.). Elimina a necessidade de reescrever código de visualização e pós-processamento para cada projeto.

## Como implementar no Hermes 2.0

```bash
pip install supervision
```

Uso básico:
```python
import supervision as sv
import cv2

# Detecção com anotação automática
image = cv2.imread("input.jpg")
detections = sv.Detections.from_yolo(model, image)

# Anotar bounding boxes
box_annotator = sv.BoundingBoxAnnotator()
annotated = box_annotator.annotate(image, detections)

# Rastreamento de objetos em vídeo
tracker = sv.ByteTrack()
tracked = tracker.update_with_detections(detections)
```

## Comandos
```bash
pip install supervision

# Verificar instalação
python -c "import supervision as sv; print(sv.__version__)"
```

## Referência
- https://github.com/roboflow/supervision
- Fonte: GitHub Trending
