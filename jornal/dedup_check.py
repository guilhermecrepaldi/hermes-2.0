#!/usr/bin/env python3
"""Analyze duplicate news across editions"""
import re
from difflib import SequenceMatcher

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all cards with titles and detail content
pattern = r'<article[^>]*data-id="([^"]+)"[^>]*>.*?<h3>(.*?)</h3>.*?<div class="detail-content">(.*?)</div>'
matches = re.findall(pattern, html, re.DOTALL)

# Group by edition
by_ed = {}
for cid, title, detail in matches:
    title_clean = re.sub(r'<[^>]+>', '', title).strip()
    detail_clean = re.sub(r'<[^>]+>', '', detail).strip()
    ed = cid.split('-')[1]
    by_ed.setdefault(ed, []).append({
        'id': cid, 'title': title_clean, 'detail': detail_clean[:200]
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

for i in range(len(eds)):
    for j in range(i+1, len(eds)):
        ed1, ed2 = eds[i], eds[j]
        cards1, cards2 = by_ed[ed1], by_ed[ed2]

        for idx1, c1 in enumerate(cards1):
            t1 = re.sub(r'[^a-z0-9\s]', '', c1['title'].lower()).strip()[:60]
            if len(t1) < 10:
                continue

            for idx2, c2 in enumerate(cards2):
                t2 = re.sub(r'[^a-z0-9\s]', '', c2['title'].lower()).strip()[:60]
                if len(t2) < 10:
                    continue

                # Check title similarity
                ratio = SequenceMatcher(None, t1, t2).ratio()

                # Also check detail content if titles are short/similar
                if ratio > 0.40:
                    d1 = re.sub(r'[^a-z0-9\s]', '', c1['detail'][:150].lower())
                    d2 = re.sub(r'[^a-z0-9\s]', '', c2['detail'][:150].lower())
                    detail_ratio = SequenceMatcher(None, d1, d2).ratio() if len(d1) > 20 and len(d2) > 20 else 0

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
