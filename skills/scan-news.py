#!/usr/bin/env python3
"""
scan-news.py — Varredura diária simplificada de notícias de IA
--------------------------------------------------------------
Gera JSON pronto pra importar no Jornal do site (/admin/news.php).

Uso:  python scan-news.py
Saída: ~/news_exports/news_export_YYYYMMDD_HHMMSS.json
"""

import json, os, sys
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
from pathlib import Path
import ssl
import re

OUTPUT_DIR = Path("D:/projetos/guilherme-portfolio/news_exports")

SOURCES = [
    ("HuggingFace Papers", "https://huggingface.co/papers"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/"),
    ("ArsTechnica AI", "https://arstechnica.com/information-technology/"),
]

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def fetch(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15, context=ssl_ctx) as r:
            return r.read().decode('utf-8', errors='ignore')
    except:
        return None

def extract_titles(html, source_name):
    if not html:
        return []
    titles = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html, re.DOTALL)
    results = []
    for t in titles:
        t = re.sub(r'<[^>]+>', '', t).strip()
        if len(t) < 15 or len(t) > 200:
            continue
        if any(kw in t.lower() for kw in ['cookie', 'privacy', 'subscribe']):
            continue
        results.append(t)
    return results[:8]

def classify_type(title):
    t = title.lower()
    if any(w in t for w in ['lanc', 'release', 'beta', 'novo', 'disponivel']):
        return 'novidade'
    elif any(w in t for w in ['pesquisa', 'paper', 'estudo', 'cientistas', 'descoberta']):
        return 'descoberta'
    elif any(w in t for w in ['ferramenta', 'app', 'codigo', 'github', 'open source']):
        return 'projeto'
    elif any(w in t for w in ['tutorial', 'guia', 'aprenda', 'como']):
        return 'aprendizado'
    else:
        return 'novidade'

def make_content(title, source_name):
    """
    Gera conteudo em portugues usando Ollama ou fallback contextual.
    """
    import subprocess, json as _json
    
    prompt = (
        f'Explique em DUAS frases em portugues brasileiro, em tom de noticia de jornal, '
        f'o seguinte fato: "{title}". '
        f'Escreva de forma simples e direta. Apenas as duas frases.')
    
    try:
        proc = subprocess.run(
            ['ollama', 'run', 'qwen2.5-coder:7b', prompt],
            capture_output=True, text=True, timeout=25
        )
        texto = proc.stdout.strip().split('\\n')[0].strip()
        if len(texto) < 40:
            texto = ''
    except:
        texto = ''
    
    if not texto:
        # Fallback contextual baseado em palavras-chave
        t = title.lower()
        palavras = t.split()
        ctx_map = {
            'chip': 'Uma nova geracao de processadores para inteligencia artificial esta chegando ao mercado, prometendo mais velocidade e eficiencia.',
            'nvidia': 'A NVIDIA continua expandindo sua presenca no mercado de inteligencia artificial com novos anuncios e parcerias estrategicas.',
            'openai': 'A OpenAI, criadora do ChatGPT, anunciou novidades em seus modelos de inteligencia artificial, mantendo-se na lideranca do setor.',
            'anthropic': 'A Anthropic, empresa do assistente Claude, fez movimentacoes importantes no mercado de inteligencia artificial.',
            'google': 'O Google segue investindo pesado em inteligencia artificial, lancando novos recursos e modelos regularmente.',
            'apple': 'A Apple esta integrando inteligencia artificial em seus dispositivos de formas inovadoras.',
            'meta': 'A Meta, dona do Facebook, anunciou novas ferramentas e modelos de inteligencia artificial.',
            'microsoft': 'A Microsoft expande suas capacidades de IA, integrando a tecnologia em Windows, Office e Azure.',
            'salesforce': 'A Salesforce fez uma grande jogada no mercado de inteligencia artificial empresarial.',
            'spacex': 'A SpaceX, empresa de exploracao espacial, tambem esta entrando no mercado de inteligencia artificial.',
            'startup': 'Uma startup de tecnologia anunciou novidades no setor de inteligencia artificial.',
            'pesquisa': 'Pesquisadores publicaram um estudo importante na area de inteligencia artificial.',
            'modelo': 'Um novo modelo de inteligencia artificial foi lancado, prometendo desempenho superior.',
        }
        texto = 'Novidades importantes movimentam o setor de tecnologia e inteligencia artificial.'
        for key, val in ctx_map.items():
            if key in palavras:
                texto = val
                break
    
    texto = texto.replace('"', "'").replace('\\n', ' ').strip()
    
    nivel = '📌 **INFORMATIVO**\\n\\n'
    if any(w in title.lower() for w in ['alerta','crise','limita','governo','processo','law']):
        nivel = '🔥 **IMPORTANTE**\\n\\n'
    elif any(w in title.lower() for w in ['lanc','atinge','nova','record','raises','billion','supera','anunci','conquista']):
        nivel = '⚡ **DESTAQUE**\\n\\n'
    
    return f'{nivel}📰 **O que aconteceu:**\\n{texto}\\n\\n💡 **Por que isso importa:**\\nAcompanhar essas mudancas ajuda a entender para onde a tecnologia esta caminhando e como isso afeta o dia a dia.\\n\\n📎 **Fonte:** {source_name}'

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    news = []
    seen_titles = set()

    print("🔍 Escaneando " + str(len(SOURCES)) + " fontes...")

    for source_name, url in SOURCES:
        print("  → " + source_name + "...", end=" ", flush=True)
        html = fetch(url)
        if not html:
            print("❌")
            continue

        titles = extract_titles(html, source_name)
        if not titles:
            print("⚠️")
            continue

        for title in titles:
            key = title.lower().strip()
            if key in seen_titles:
                continue
            seen_titles.add(key)
            news.append({
                'titulo': title,
                'tipo': classify_type(title),
                'conteudo': make_content(title, source_name),
                'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
            })
        print("✅ " + str(len(titles)))

    ordem = {'novidade': 0, 'descoberta': 1, 'projeto': 2, 'aprendizado': 3}
    news.sort(key=lambda x: ordem.get(x['tipo'], 99))

    if not news:
        print("\n❌ Nenhuma noticia encontrada.")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / ("news_export_" + ts + ".json")
    out_path.write_text(json.dumps(news, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n✅ " + str(len(news)) + " noticias extraidas!")
    print("📁 " + str(out_path))
    print()
    print("🚀 Proximo passo:")
    print("   1. Acesse SEUSITE.COM/admin/news.php")
    print("   2. Secao 📥 Importar lote (JSON)")
    print("   3. Selecione o arquivo gerado")
    print("   4. Clique em Importar")
    print()
    for t in ['novidade', 'descoberta', 'projeto', 'aprendizado']:
        count = sum(1 for n in news if n['tipo'] == t)
        if count:
            print("   " + t + ": " + str(count))

if __name__ == "__main__":
    main()
