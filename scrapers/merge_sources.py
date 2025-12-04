#!/usr/bin/env python3
"""Merge Behance/Dribbble/AdsOfWorld JSON into master_dataset.csv"""
import json, pandas as pd
from pathlib import Path
from config import OUTPUT_DIR

def merge_all_sources():
    master_path = OUTPUT_DIR / "master_dataset.csv"
    df = pd.read_csv(master_path, low_memory=False) if master_path.exists() else pd.DataFrame()
    if 'source' not in df.columns: df['source'] = 'pinterest'  # Tag existing as Pinterest
    existing_hashes = set(df['content_hash'].dropna().astype(str))
    print(f"📁 现有数据: {len(df)} 条, {len(existing_hashes)} 个唯一 hash")
    
    sources = [('behance', 'behance_dataset.json'), ('dribbble', 'dribbble_dataset.json'), ('adsoftheworld', 'adsoftheworld_dataset.json')]
    new_rows = []
    for src, fname in sources:
        fpath = OUTPUT_DIR / fname
        if not fpath.exists(): continue
        data = json.load(open(fpath))
        added = 0
        for item in data:
            h = item.get('content_hash', '')
            if h and h not in existing_hashes:
                new_rows.append({
                    'url': item.get('url', ''), 'pin_url': item.get('page_url', ''), 'category': item.get('category', item.get('search_term', '')),
                    'category_type': item.get('category_type', 'design'), 'search_term': item.get('search_term', ''), 'title': item.get('title', ''),
                    'alt_text': '', 'saves': 0, 'comments': 0, 'engagement_score': 0, 'content_hash': h,
                    'collected_at': item.get('collected_at', ''), 'source': src
                })
                existing_hashes.add(h)
                added += 1
        print(f"  ✅ {src}: +{added} 条 (去重后)")
    
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_csv(master_path, index=False)
        print(f"\n📊 合并后总数: {len(df)} 条")
    else:
        print("\n⚠️ 没有新数据需要合并")
    return len(new_rows)

if __name__ == "__main__":
    merge_all_sources()

