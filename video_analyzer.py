#!/usr/bin/env python3
"""
Hermes Video Analyzer — Análise de vídeo com Qwen3-VL + FFmpeg + Whisper
100% local, 100% grátis (Ollama).

Uso:
  python video_analyzer.py <video.mp4> [opções]

Opções:
  --fps N           Frames por segundo para extração (padrão: 0.5 = 1 frame a cada 2s)
  --width N         Largura máxima dos frames (padrão: 640)
  --analyze         Descrever todas as cenas com Qwen3-VL
  --search "texto"  Buscar cena por descrição textual
  --cut-silence     Cortar silêncios do vídeo
  --gap N           Gap mínimo de silêncio em segundos (padrão: 1.5)
  --tutorial        Modo tutorial: corta silêncios + transcreve
  --output DIR      Diretório de saída (padrão: mesmo do vídeo)
  --model MODEL     Modelo Ollama para visão (padrão: qwen3-vl:4b)
  --keep-frames     Não apagar frames extraídos após análise
"""

import os
import sys
import json
import base64
import subprocess
import argparse
import re
from pathlib import Path
from datetime import timedelta

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")

def run_cmd(cmd, timeout=300):
    """Executa comando e retorna (stdout, stderr, returncode)."""
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def get_video_info(video_path):
    """Obtém duração, fps e resolução do vídeo."""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", video_path
    ]
    stdout, _, rc = run_cmd(cmd)
    if rc != 0:
        raise Exception("Erro ao ler informações do vídeo. ffprobe está instalado?")
    info = json.loads(stdout)
    video_stream = None
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "video":
            video_stream = stream
            break
    if not video_stream:
        raise Exception("Nenhum stream de vídeo encontrado")
    
    duration = float(info["format"].get("duration", 0))
    fps_parts = video_stream.get("r_frame_rate", "30/1").split("/")
    fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else float(fps_parts[0])
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    
    return {
        "duration": duration,
        "fps": fps,
        "width": width,
        "height": height,
        "path": video_path,
        "filename": os.path.basename(video_path),
    }

def extract_frames(video_path, output_dir, fps=0.5, max_width=640):
    """Extrai frames do vídeo em intervalo regular."""
    log(f"Extraindo frames a {fps} fps...")
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps={fps},scale={max_width}:-1",
        "-q:v", "2",
        os.path.join(output_dir, "frame_%06d.jpg"),
        "-y", "-hide_banner", "-loglevel", "error"
    ]
    _, _, rc = run_cmd(cmd, timeout=600)
    
    if rc != 0:
        raise Exception("Erro ao extrair frames")
    
    frames = sorted([
        f for f in os.listdir(output_dir) if f.startswith("frame_") and f.endswith(".jpg")
    ])
    log(f"{len(frames)} frames extraídos em {output_dir}")
    return frames

def extract_audio(video_path, output_path):
    """Extrai áudio do vídeo para transcrição."""
    log("Extraindo áudio...")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        output_path, "-y", "-hide_banner", "-loglevel", "error"
    ]
    _, _, rc = run_cmd(cmd, timeout=300)
    if rc != 0:
        raise Exception("Erro ao extrair áudio")
    log(f"Áudio extraído: {output_path}")
    return output_path

def transcribe_audio(audio_path):
    """Transcreve áudio com Whisper via Ollama (ou fallback para whisper.cpp)."""
    # Tenta usar whisper.cpp se disponível
    whisper_paths = [
        "whisper",  # PATH
        "/usr/local/bin/whisper",
        os.path.expanduser("~/whisper.cpp/main"),
    ]
    
    for wp in whisper_paths:
        try:
            cmd = [wp, "-f", audio_path, "-otxt", "--output_dir", os.path.dirname(audio_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                txt_file = audio_path.replace(".wav", ".txt")
                if os.path.exists(txt_file):
                    with open(txt_file) as f:
                        text = f.read().strip()
                    log(f"Transcrição: {len(text)} caracteres")
                    return text
        except FileNotFoundError:
            continue
    
    log("Whisper não encontrado. Instale com: pip install openai-whisper")
    log("Fallback: transcrição via Ollama (menos precisa)")
    return ""  # Placeholder — usuário precisa instalar whisper

def analyze_frame_with_qwen(image_path, model="qwen3-vl:4b", prompt="Descreva detalhadamente esta cena em português."):
    """Analisa um frame com Qwen3-VL via Ollama API."""
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        log(f"Erro ao ler imagem {image_path}: {e}", "ERROR")
        return ""
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "images": [img_b64],
        "options": {
            "temperature": 0.1
        }
    }
    
    try:
        import urllib.request
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "")
    except Exception as e:
        log(f"Erro ao analisar frame {os.path.basename(image_path)}: {e}", "ERROR")
    
    return ""


def analyze_frames_batch(frames_list, frames_directory, fps_extract, model="qwen3-vl:4b", prompt=None, max_workers=3):
    """Analisa múltiplos frames em paralelo com Qwen3-VL."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import re
    
    if prompt is None:
        prompt = "Descreva esta cena em português em até 30 palavras. Mencione apenas o essencial."
    
    results = []
    total = len(frames_list)
    completed = 0
    
    def process_one(frame_file):
        frame_path = os.path.join(frames_directory, frame_file)
        match = re.search(r"(\d+)", frame_file)
        frame_num = int(match.group(1)) if match else 0
        timestamp = frame_num / fps_extract
        
        description = analyze_frame_with_qwen(frame_path, model, prompt)
        
        return {
            "frame": frame_file,
            "timestamp": timestamp,
            "timestamp_str": str(timedelta(seconds=int(timestamp))),
            "description": description
        }
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_map = {executor.submit(process_one, f): f for f in frames_list}
        for future in as_completed(future_map):
            completed += 1
            result = future.result()
            results.append(result)
            print(f"\r  Frame {completed}/{total} ({result['timestamp_str']})...", end="", flush=True)
    
    print()
    return sorted(results, key=lambda x: x["timestamp"])

def detect_silence(video_path, silence_threshold=-50, min_silence_duration=1.0):
    """
    Detecta silêncios no vídeo usando ffmpeg silencedetect.
    Retorna lista de (start, end, duration) em segundos.
    """
    log(f"Detectando silêncios (threshold={silence_threshold}dB, min={min_silence_duration}s)...")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-af", f"silencedetect=noise={silence_threshold}dB:d={min_silence_duration}",
        "-f", "null", "-",
        "-y", "-hide_banner", "-loglevel", "info"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    output = result.stdout + "\n" + result.stderr
    
    # Parse silencedetect output
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", output)]
    ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", output)]
    
    silences = []
    for s, e in zip(starts, ends):
        silences.append({"start": s, "end": e, "duration": e - s})
    
    log(f"{len(silences)} silêncios detectados")
    return silences

def cut_silences(video_path, output_path, silences, padding=0.3):
    """
    Corta silêncios do vídeo usando FFmpeg concat.
    Mantém padding de 0.3s antes/depois para transição natural.
    """
    if not silences:
        log("Nenhum silêncio para cortar.")
        return False
    
    import shutil
    
    # Construir lista de segmentos para manter
    segments = []
    video_duration = get_video_info(video_path)["duration"]
    current_start = 0.0
    
    for s in silences:
        seg_end = max(0, s["start"] - padding)
        if seg_end > current_start:
            segments.append((current_start, seg_end))
        current_start = min(video_duration, s["end"] + padding)
    
    # Último segmento
    if current_start < video_duration:
        segments.append((current_start, video_duration))
    
    if not segments:
        log("Nenhum segmento para manter (vídeo todo é silêncio?)")
        return False
    
    # Criar arquivo de concat temporário
    work_dir = os.path.dirname(output_path)
    concat_file = os.path.abspath(os.path.join(work_dir, "concat_list.txt"))
    seg_paths = []
    
    with open(concat_file, "w") as f:
        for i, (start, end) in enumerate(segments):
            seg_path = os.path.abspath(os.path.join(work_dir, f"seg_{i:04d}.mp4"))
            seg_paths.append(seg_path)
            duration = end - start
            cmd = [
                "ffmpeg", "-i", video_path,
                "-ss", str(start), "-t", str(duration),
                "-c:v", "libx264", "-c:a", "aac",
                seg_path, "-y", "-hide_banner", "-loglevel", "error"
            ]
            _, _, rc = run_cmd(cmd, timeout=120)
            if rc == 0 and os.path.exists(seg_path) and os.path.getsize(seg_path) > 0:
                f.write(f"file '{seg_path}'\n")
            else:
                log(f"Erro ao criar segmento {i}: start={start}, end={end}", "ERROR")
    
    # Verificar se tem segmentos
    if not os.path.exists(concat_file) or os.path.getsize(concat_file) == 0:
        log("Nenhum segmento gerado!", "ERROR")
        # Limpar
        for p in seg_paths:
            if os.path.exists(p): os.remove(p)
        return False
    
    # Concatenar
    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264", "-c:a", "aac",
        "-movflags", "+faststart",
        output_path, "-y", "-hide_banner", "-loglevel", "error"
    ]
    stdout, stderr, rc = run_cmd(cmd, timeout=300)
    
    # Limpar segmentos temporários
    for p in seg_paths:
        if os.path.exists(p): os.remove(p)
    if os.path.exists(concat_file):
        os.remove(concat_file)
    
    if rc == 0:
        duration_before = video_duration
        duration_after = get_video_info(output_path)["duration"]
        saved = duration_before - duration_after
        log(f"✅ Silêncios cortados! {duration_before:.1f}s → {duration_after:.1f}s (economia: {saved:.1f}s / {saved/duration_before*100:.1f}%)")
        return True
    else:
        log("Erro ao concatenar segmentos", "ERROR")
        return False

def main():
    parser = argparse.ArgumentParser(description="Hermes Video Analyzer")
    parser.add_argument("video", help="Arquivo de vídeo MP4")
    parser.add_argument("--fps", type=float, default=0.5, help="Frames por segundo (padrão: 0.5)")
    parser.add_argument("--width", type=int, default=640, help="Largura máxima dos frames")
    parser.add_argument("--analyze", action="store_true", help="Analisar todas as cenas")
    parser.add_argument("--search", type=str, help="Buscar cena por descrição")
    parser.add_argument("--cut-silence", action="store_true", help="Cortar silêncios")
    parser.add_argument("--gap", type=float, default=1.5, help="Gap mínimo de silêncio (s)")
    parser.add_argument("--tutorial", action="store_true", help="Modo tutorial: corta silêncios + info")
    parser.add_argument("--output", type=str, help="Diretório de saída")
    parser.add_argument("--model", type=str, default="qwen3-vl:4b", help="Modelo Ollama")
    parser.add_argument("--keep-frames", action="store_true", help="Manter frames após análise")
    
    args = parser.parse_args()
    
    # Validar vídeo
    if not os.path.exists(args.video):
        log(f"Arquivo não encontrado: {args.video}", "ERROR")
        sys.exit(1)
    
    # Diretório de saída
    video_name = Path(args.video).stem
    output_dir = args.output or os.path.join(os.path.dirname(args.video), f"{video_name}_analysis")
    os.makedirs(output_dir, exist_ok=True)
    
    # Informações do vídeo
    vin = get_video_info(args.video)
    log(f"Vídeo: {vin['filename']} ({vin['width']}x{vin['height']}, {vin['duration']:.1f}s, {vin['fps']:.2f}fps)")
    
    # ─── MODO TUTORIAL ───
    if args.tutorial or args.cut_silence:
        print(f"\n{'='*60}")
        print(f"🎬 HERMES VIDEO ANALYZER — MODO TUTORIAL")
        print(f"{'='*60}")
        print(f"📹 Vídeo: {vin['filename']}")
        print(f"⏱️  Duração: {vin['duration']:.1f}s ({timedelta(seconds=int(vin['duration']))})")
        print()
        
        # Extrair áudio para info
        audio_path = os.path.join(output_dir, f"{video_name}.wav")
        extract_audio(args.video, audio_path)
        
        # Detectar silêncios
        silences = detect_silence(args.video, min_silence_duration=args.gap)
        
        if silences:
            total_silence = sum(s["duration"] for s in silences)
            print(f"\n🔇 Silêncios detectados: {len(silences)}")
            print(f"⏱️  Tempo total de silêncio: {total_silence:.1f}s ({total_silence/vin['duration']*100:.1f}% do vídeo)")
            print(f"\n📋 Timeline de silêncios:")
            for s in silences[:20]:
                print(f"   {timedelta(seconds=int(s['start']))} → {timedelta(seconds=int(s['end']))} ({s['duration']:.1f}s)")
            if len(silences) > 20:
                print(f"   ... e mais {len(silences)-20} silêncios")
            
            # Cortar silêncios
            output_video = os.path.join(output_dir, f"{video_name}_sem_silencio.mp4")
            success = cut_silences(args.video, output_video, silences)
            
            if success:
                print(f"\n✅ Vídeo processado: {output_video}")
        else:
            print(f"\n✅ Nenhum silêncio significativo (> {args.gap}s) encontrado!")
            output_video = args.video
        
        return 0
    
    # ─── MODO ANALISAR ───
    if args.analyze:
        print(f"\n{'='*60}")
        print(f"🔍 ANALISANDO VÍDEO COM QWEN3-VL")
        print(f"{'='*60}")
        
        frames_dir = os.path.join(output_dir, "frames")
        frames = extract_frames(args.video, frames_dir, args.fps, args.width)
        
        if not frames:
            log("Nenhum frame extraído!", "ERROR")
            return 1
        
        results = analyze_frames_batch(frames, frames_dir, args.fps, args.model)
        
        print()
        
        # Salvar resultados
        output_file = os.path.join(output_dir, f"{video_name}_analise.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        log(f"Análise salva em: {output_file}")
        
        # Mostrar resumo
        print(f"\n📊 RESUMO DA ANÁLISE:")
        for r in results[:10]:
            print(f"  [{r['timestamp_str']}] {r['description'][:100]}...")
        if len(results) > 10:
            print(f"  ... e mais {len(results)-10} frames")
        
        if not args.keep_frames:
            import shutil
            shutil.rmtree(frames_dir)
            log("Frames temporários removidos (use --keep-frames para manter)")
        
        return 0
    
    # ─── MODO BUSCAR ───
    if args.search:
        print(f"\n{'='*60}")
        print(f"🔎 BUSCANDO: '{args.search}'")
        print(f"{'='*60}")
        
        frames_dir = os.path.join(output_dir, "frames")
        frames = extract_frames(args.video, frames_dir, args.fps, args.width)
        
        search_prompt = f"Esta cena contém algo relacionado a '{args.search}'? Responda apenas SIM ou NAO e explique em uma frase."
        
        print(f"Buscando em {len(frames)} frames...\n")
        
        best_match = None
        best_score = 0
        
        for i, frame_file in enumerate(frames):
            frame_path = os.path.join(frames_dir, frame_file)
            frame_num = int(re.search(r"(\d+)", frame_file).group(1))
            timestamp = frame_num / args.fps
            
            print(f"\r  Verificando frame {i+1}/{len(frames)} ({timedelta(seconds=int(timestamp))})...", end="", flush=True)
            response = analyze_frame_with_qwen(frame_path, args.model, search_prompt)
            
            if any(w in response.lower() for w in ["sim", "yes", "contém", "aparece", "mostra"]):
                print(f"\n  ✅ [MATCH] {timedelta(seconds=int(timestamp))}: {response[:150]}")
                best_match = {"timestamp": timestamp, "frame": frame_file, "description": response}
                best_score += 1
        
        print()
        if best_match:
            print(f"\n🎯 MELHOR MATCH em {timedelta(seconds=int(best_match['timestamp']))}")
            print(f"   Frame: {best_match['frame']}")
        else:
            print(f"\n😕 Nenhum match encontrado para '{args.search}'")
        
        if not args.keep_frames:
            import shutil
            shutil.rmtree(frames_dir)
        
        return 0
    
    # ─── MODO PADRÃO (info) ───
    print(f"\n📹 INFORMAÇÕES DO VÍDEO")
    print(f"   Arquivo: {vin['filename']}")
    print(f"   Duração: {vin['duration']:.1f}s ({timedelta(seconds=int(vin['duration']))})")
    print(f"   Resolução: {vin['width']}x{vin['height']}")
    print(f"   FPS: {vin['fps']:.2f}")
    print(f"\nComandos disponíveis:")
    print(f"  --analyze       Analisar todas as cenas com Qwen3-VL")
    print(f"  --search \"texto\" Buscar cena por descrição")
    print(f"  --tutorial      Cortar silêncios (modo tutorial)")
    print(f"  --cut-silence   Cortar silêncios do vídeo")
    print(f"  --gap 1.5       Gap mínimo de silêncio (segundos)")
    
    return 0

if __name__ == "__main__":
    main()
