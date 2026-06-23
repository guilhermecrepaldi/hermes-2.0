#!/usr/bin/env python3
"""Dedup filter for TOP OF THE HOUR news cards.
Checks if a potential new card already exists in the HTML across ALL editions.
Usage: python dedup_filter.py "NVIDIA Blackwell Ultra 50x Performance" "NVIDIA announced..."
Returns: DUPLICATE|UNIQUE [confidence%] [matching_edition]
"""
import re
import sys
from difflib import SequenceMatcher

HTML_PATH = "D:/projetos/TOP OF THE HOUR - IA/index.html"

def check_duplicate(new_title, new_detail=""):
    """Check if a potential new card is a duplicate of existing ones."""
    try:
        with open(HTML_PATH, 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        return "NO_FILE", 0, ""

    # Extract existing cards
    pattern = r'<article[^>]*data-id="([^"]+)"[^>]*>.*?<h3>(.*?)</h3>.*?<div class="detail-content">(.*?)</div>'
    matches = re.findall(pattern, html, re.DOTALL)

    new_title_clean = re.sub(r'[^a-z0-9\s]', '', new_title.lower()).strip()[:80]
    new_detail_clean = re.sub(r'[^a-z0-9\s]', '', new_detail.lower()).strip()[:200]

    best_match = ("", 0, "")

    for cid, title, detail in matches:
        title_clean = re.sub(r'<[^>]+>', '', title).strip()[:80].lower()
        title_clean = re.sub(r'[^a-z0-9\s]', '', title_clean)
        detail_clean = re.sub(r'<[^>]+>', '', detail).strip()[:200].lower()
        detail_clean = re.sub(r'[^a-z0-9\s]', '', detail_clean)

        ed = cid.split('-')[1] if '-' in cid else "?"

        # Title similarity
        title_ratio = SequenceMatcher(None, new_title_clean, title_clean).ratio()

        # Detail similarity
        detail_ratio = 0
        if len(new_detail_clean) > 30 and len(detail_clean) > 30:
            detail_ratio = SequenceMatcher(None, new_detail_clean, detail_clean).ratio()

        # Combined score
        combined = max(title_ratio, detail_ratio * 0.8)

        if combined > best_match[1]:
            best_match = (ed, combined, title[:60])

    return best_match


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dedup_filter.py 'TITLE' ['DETAIL_TEXT']")
        sys.exit(1)

    new_title = sys.argv[1]
    new_detail = sys.argv[2] if len(sys.argv) > 2 else ""

    ed, score, match_title = check_duplicate(new_title, new_detail)

    threshold = 0.55  # Adjust: higher = fewer false positives

    if score >= threshold:
        print(f"DUPLICATE|{score:.0%}|Ed.{ed}|{match_title}")
    else:
        print(f"UNIQUE|{score:.0%}|")
