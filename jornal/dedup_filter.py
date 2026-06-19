#!/usr/bin/env python3
"""Dedup filter for TOP OF THE HOUR news cards - OPTIMIZED VERSION.
Checks if a potential new card already exists in the HTML across ALL editions.
Usage: python dedup_filter.py "NVIDIA Blackwell Ultra 50x Performance" "NVIDIA announced..."
Returns: DUPLICATE|UNIQUE [confidence%] [matching_edition]
"""
import sys
import re
from difflib import SequenceMatcher

# Pre-compile regex patterns
CARD_PATTERN = re.compile(
    r'<article[^>]*data-id="([^"]+)"[^>]*>.*?<h3>(.*?)</h3>.*?<div class="detail-content">(.*?)</div>',
    re.DOTALL
)
TAG_STRIP_PATTERN = re.compile(r'<[^>]+>')
NON_ALNUM_PATTERN = re.compile(r'[^a-z0-9\s]', re.IGNORECASE)

HTML_PATH = "D:/projetos/TOP OF THE HOUR - IA/index.html"

def clean_text(text, max_len=None):
    """Strip HTML tags and normalize text efficiently."""
    cleaned = TAG_STRIP_PATTERN.sub('', text).strip().lower()
    cleaned = NON_ALNUM_PATTERN.sub('', cleaned).strip()
    if max_len:
        cleaned = cleaned[:max_len]
    return cleaned

def check_duplicate(new_title, new_detail=""):
    """Check if a potential new card is a duplicate of existing ones."""
    try:
        with open(HTML_PATH, 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        return ("NO_FILE", 0, "")
    
    # Extract existing cards using pre-compiled pattern
    matches = CARD_PATTERN.findall(html)
    
    new_title_clean = clean_text(new_title, 80)
    new_detail_clean = clean_text(new_detail, 200)
    
    best_match = ("", 0, "")
    
    # Cache for similarity computations
    title_cache = {}
    detail_cache = {}
    
    for cid, title, detail in matches:
        title_clean = clean_text(title, 80)
        detail_clean = clean_text(detail, 200)
        
        ed = cid.split('-')[1] if '-' in cid else "?"
        
        # Title similarity with caching
        if title_clean not in title_cache:
            title_cache[title_clean] = SequenceMatcher(None, new_title_clean, title_clean).ratio()
        title_ratio = title_cache[title_clean]
        
        # Detail similarity with caching
        detail_ratio = 0
        if len(new_detail_clean) > 30 and len(detail_clean) > 30:
            cache_key = (new_detail_clean, detail_clean)
            if cache_key in detail_cache:
                detail_ratio = detail_cache[cache_key]
            else:
                detail_ratio = SequenceMatcher(None, new_detail_clean, detail_clean).ratio()
                detail_cache[cache_key] = detail_ratio
        
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
