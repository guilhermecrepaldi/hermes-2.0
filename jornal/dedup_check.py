#!/usr/bin/env python3
"""Analyze duplicate news across editions - OPTIMIZED VERSION"""
import re
from difflib import SequenceMatcher

# Pre-compile regex patterns for better performance
CARD_PATTERN = re.compile(
    r'<article[^>]*data-id="([^"]+)"[^>]*>.*?<h3>(.*?)</h3>.*?<div class="detail-content">(.*?)</div>',
    re.DOTALL
)
TAG_STRIP_PATTERN = re.compile(r'<[^>]+>')
NON_ALNUM_PATTERN = re.compile(r'[^a-z0-9\s]', re.IGNORECASE)

def clean_text(text, max_len=None):
    """Strip HTML tags and normalize text efficiently."""
    cleaned = TAG_STRIP_PATTERN.sub('', text).strip().lower()
    cleaned = NON_ALNUM_PATTERN.sub('', cleaned).strip()
    if max_len:
        cleaned = cleaned[:max_len]
    return cleaned

def main():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        print("Error: index.html not found")
        return
    
    # Extract all cards with titles and detail content
    matches = CARD_PATTERN.findall(html)
    
    # Group by edition
    by_ed = {}
    for cid, title, detail in matches:
        ed = cid.split('-')[1]
        by_ed.setdefault(ed, []).append({
            'id': cid, 
            'title': clean_text(title), 
            'detail': clean_text(detail, 200)
        })
    
    print("CARDS PER EDITION:")
    for ed in sorted(by_ed.keys()):
        print(f"  Ed. {ed}: {len(by_ed[ed])} cards")
    
    print("\n" + "="*70)
    print("DUPLICATE ANALYSIS (cross-edition)")
    print("="*70)
    
    eds = sorted(by_ed.keys())
    dup_total = 0
    
    # Track which cards to remove
    remove_ids = set()
    
    # Cache for already computed similarities
    similarity_cache = {}
    
    for i in range(len(eds)):
        for j in range(i+1, len(eds)):
            ed1, ed2 = eds[i], eds[j]
            cards1, cards2 = by_ed[ed1], by_ed[ed2]
            
            for idx1, c1 in enumerate(cards1):
                t1 = c1['title'][:60]
                if len(t1) < 10:
                    continue
                    
                for idx2, c2 in enumerate(cards2):
                    t2 = c2['title'][:60]
                    if len(t2) < 10:
                        continue
                    
                    # Check title similarity with caching
                    cache_key = (t1, t2)
                    if cache_key in similarity_cache:
                        ratio = similarity_cache[cache_key]
                    else:
                        ratio = SequenceMatcher(None, t1, t2).ratio()
                        similarity_cache[cache_key] = ratio
                    
                    # Also check detail content if titles are short/similar
                    if ratio > 0.40:
                        d1 = c1['detail'][:150]
                        d2 = c2['detail'][:150]
                        
                        detail_cache_key = (d1, d2)
                        if detail_cache_key in similarity_cache:
                            detail_ratio = similarity_cache[detail_cache_key]
                        else:
                            detail_ratio = SequenceMatcher(None, d1, d2).ratio() if len(d1) > 20 and len(d2) > 20 else 0
                            similarity_cache[detail_cache_key] = detail_ratio
                        
                        if ratio > 0.55 or detail_ratio > 0.50 or (ratio > 0.40 and detail_ratio > 0.40):
                            dup_total += 1
                            # Mark the OLDER edition's card for removal
                            if ed1 < ed2:
                                remove_ids.add(c1['id'])
                            else:
                                remove_ids.add(c2['id'])
                            print(f"\n  [{ed1}] {c1['title'][:65]}")
                            print(f"  [{ed2}] {c2['title'][:65]}")
                            print(f"  Title match: {ratio:.0%} | Detail match: {detail_ratio:.0%}")
                            break
    
    print(f"\n{'='*70}")
    print(f"DUPLICATE PAIRS FOUND: {dup_total}")
    print(f"CARDS TO REMOVE (older edition): {len(remove_ids)}")
    print(f"IDs: {sorted(remove_ids)[:10]}...")

if __name__ == "__main__":
    main()
