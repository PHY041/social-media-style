#!/usr/bin/env python3
"""Prompt Search: 利用现有 V3 Prompt 字段进行多维度搜索"""
import json, re, sys
from pathlib import Path
from typing import Optional
sys.path.insert(0, str(Path(__file__).parent.parent))

VLM_RESULTS = Path(__file__).parent.parent / "output" / "vlm_results_v3.json"
_prompts: Optional[list] = None

def load_prompts() -> list[dict]:
    global _prompts
    if _prompts is None:
        with open(VLM_RESULTS) as f: data = json.load(f)
        _prompts = [{"content_hash": r["content_hash"], "image_url": r["image_url"], "cluster_id": r.get("cluster_id"), "prompt": r["result"]} for r in data if r.get("status") == "success"]
    return _prompts

def extract_searchable_fields(prompt: dict) -> dict:
    """从 prompt 提取可搜索字段"""
    p = prompt.get('prompt', prompt)
    scene = p.get('scene', {})
    return {
        "image_style": p.get('image_style', '').lower(),
        "subject_type": scene.get('subject', {}).get('type', '').lower(),
        "subject_desc": scene.get('subject', {}).get('description', '').lower(),
        "lighting_type": scene.get('lighting', {}).get('type', '').lower(),
        "lighting_quality": scene.get('lighting', {}).get('quality', '').lower(),
        "color_tone": p.get('color_palette', {}).get('tone', '').lower(),
        "dominant_colors": [c.lower() for c in p.get('color_palette', {}).get('dominant', [])],
        "mood_keywords": [m.lower() for m in p.get('mood_keywords', [])],
        "intended_use": p.get('intended_use', '').lower(),
        "background": scene.get('environment', {}).get('background', '').lower()
    }

def score_match(query: dict, fields: dict) -> float:
    """计算查询与 prompt 的匹配分数"""
    score = 0.0
    
    # subject_type 精确匹配 (权重高)
    if query.get('subject_type') and query['subject_type'] in fields['subject_type']: score += 3.0
    
    # intended_use 包含匹配 (权重高)
    if query.get('industry'):
        industry_keywords = query['industry'].lower().split()
        for kw in industry_keywords:
            if kw in fields['intended_use']: score += 2.0
    
    # mood 匹配
    if query.get('mood'):
        query_moods = query['mood'].lower().split() if isinstance(query['mood'], str) else [m.lower() for m in query['mood']]
        for qm in query_moods:
            for fm in fields['mood_keywords']:
                if qm in fm or fm in qm: score += 1.5
    
    # color_tone 匹配
    if query.get('color_tone') and query['color_tone'].lower() in fields['color_tone']: score += 1.0
    
    # lighting 匹配
    if query.get('lighting'):
        if query['lighting'].lower() in fields['lighting_type']: score += 1.0
        if query['lighting'].lower() in fields['lighting_quality']: score += 0.5
    
    # 自由文本搜索 (image_style, subject_desc, background)
    if query.get('keywords'):
        keywords = query['keywords'].lower().split() if isinstance(query['keywords'], str) else query['keywords']
        text_fields = fields['image_style'] + ' ' + fields['subject_desc'] + ' ' + fields['background']
        for kw in keywords:
            if kw in text_fields: score += 0.5
    
    return score

def search_prompts(
    subject_type: str = None,      # "human", "product", "food"
    industry: str = None,          # "fashion", "wellness", "food", "beauty"
    mood: str = None,              # "warm", "minimalist", "elegant"
    color_tone: str = None,        # "warm", "cool"
    lighting: str = None,          # "soft", "natural", "studio"
    keywords: str = None,          # 自由文本搜索
    top_k: int = 5
) -> list[dict]:
    """多维度搜索 prompts"""
    prompts = load_prompts()
    query = {"subject_type": subject_type, "industry": industry, "mood": mood, "color_tone": color_tone, "lighting": lighting, "keywords": keywords}
    query = {k: v for k, v in query.items() if v}  # 移除 None 值
    if not query: return prompts[:top_k]  # 无查询条件，返回前 K 个
    
    scored = []
    for p in prompts:
        fields = extract_searchable_fields(p)
        score = score_match(query, fields)
        if score > 0: scored.append((score, p))
    
    scored.sort(key=lambda x: -x[0])
    return [{"score": s, **p} for s, p in scored[:top_k]]

def prompt_to_fal_text(prompt: dict) -> str:
    """将 V3 Prompt 转为 FAL 可用的文本"""
    p = prompt.get('prompt', prompt)
    scene = p.get('scene', {})
    subject = scene.get('subject', {})
    lighting = scene.get('lighting', {})
    env = scene.get('environment', {})
    comp = p.get('composition', {})
    palette = p.get('color_palette', {})
    
    parts = [
        p.get('image_style', ''),
        f"Subject: {subject.get('description', '')}." if subject.get('description') else "",
        f"Lighting: {lighting.get('quality', '')} {lighting.get('type', '')}." if lighting.get('type') else "",
        f"Background: {env.get('background', '')}." if env.get('background') else "",
        f"Composition: {comp.get('framing', '')}, {comp.get('camera_angle', '')}." if comp.get('framing') else "",
        f"Color: {palette.get('tone', '')} tones with {', '.join(palette.get('dominant', [])[:3])}." if palette.get('dominant') else "",
        f"Mood: {', '.join(p.get('mood_keywords', [])[:4])}." if p.get('mood_keywords') else ""
    ]
    return " ".join(p for p in parts if p)

# === EXAMPLE USAGE ===
if __name__ == "__main__":
    print("=== 搜索示例 1: Wellness + Human + Warm ===\n")
    results = search_prompts(subject_type="human", industry="wellness fitness", mood="serene calm", top_k=3)
    for i, r in enumerate(results, 1):
        print(f"--- Result {i} (score: {r['score']:.1f}) ---")
        print(f"Image URL: {r['image_url'][:60]}...")
        print(f"Style: {r['prompt'].get('image_style', '')[:80]}...")
        print(f"Intended Use: {r['prompt'].get('intended_use', '')}")
        print()
    
    print("\n=== 搜索示例 2: Fashion + Product + Elegant ===\n")
    results = search_prompts(subject_type="product", industry="fashion luxury", mood="elegant premium", color_tone="warm", top_k=3)
    for i, r in enumerate(results, 1):
        print(f"--- Result {i} (score: {r['score']:.1f}) ---")
        print(f"Style: {r['prompt'].get('image_style', '')[:80]}...")
        print(f"Mood: {r['prompt'].get('mood_keywords', [])}")
        print()
    
    print("\n=== FAL Prompt Text (第一个结果) ===")
    if results:
        print(prompt_to_fal_text(results[0]))
