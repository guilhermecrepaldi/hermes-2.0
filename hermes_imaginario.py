#!/usr/bin/env python3
"""
HERMES IMAGINATOR — Geração de imagens local
Usa Stable Diffusion 1.5 (leve, ~2GB, roda em 4GB VRAM)

Uso:
  python hermes_imaginario.py "um gato astronauta no espaço"
  python hermes_imaginario.py "paisagem cyberpunk" --output minha_img.png
  python hermes_imaginario.py "logo minimalista" --steps 20
"""

import sys
import os
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="🎨 Hermes Imaginário — Geração de Imagens Local")
    parser.add_argument("prompt", nargs="?", help="Descrição da imagem")
    parser.add_argument("--output", "-o", default=None, help="Arquivo de saída")
    parser.add_argument("--steps", type=int, default=25, help="Passos de inferência (padrão: 25)")
    parser.add_argument("--model", default="runwayml/stable-diffusion-v1-5", help="Modelo HF")
    parser.add_argument("--device", default="cuda", help="device: cuda ou cpu")
    
    args = parser.parse_args()
    
    if not args.prompt:
        args.prompt = input("🎨 Descreva a imagem que quer gerar: ")
    
    output = args.output or f"imagem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    print(f"\n{'='*60}")
    print(f"🎨 HERMES IMAGINÁRIO — Gerando imagem")
    print(f"{'='*60}")
    print(f"📝 Prompt: {args.prompt}")
    print(f"⚙️  Modelo: {args.model}")
    print(f"🔄 Passos: {args.steps}")
    print(f"💾 Saída: {output}")
    
    try:
        import torch
        from diffusers import StableDiffusionPipeline
        
        print(f"\n📥 Carregando modelo (primeira vez baixa ~2GB)...")
        
        pipe = StableDiffusionPipeline.from_pretrained(
            args.model,
            torch_dtype=torch.float16 if args.device == "cuda" else torch.float32,
            safety_checker=None,
        )
        pipe = pipe.to(args.device)
        
        if args.device == "cuda":
            pipe.enable_attention_slicing()
        
        print(f"🎨 Gerando...")
        image = pipe(
            args.prompt,
            num_inference_steps=args.steps,
            guidance_scale=7.5,
        ).images[0]
        
        image.save(output)
        print(f"✅ Imagem salva: {output}")
        
        # Mostrar preview no terminal (ASCII aproximado)
        print(f"\n📐 {image.size[0]}x{image.size[1]}px")
        
    except ImportError as e:
        print(f"\n❌ Erro: {e}")
        print("   Execute: pip install diffusers transformers torch accelerate")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
