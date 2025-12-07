#!/usr/bin/env python3
"""Style Service: 完整的 Prompt 生成服务"""
import json, os, sys
from pathlib import Path
from typing import Optional
from openai import OpenAI
sys.path.insert(0, str(Path(__file__).parent.parent))
from api.prompt_search import search_prompts, prompt_to_fal_text

def parse_request_to_query(brand: dict, campaign: dict, request: dict) -> dict:
    """解析请求生成搜索 Query"""
    content_type = request.get('content_type', 'hero_shot')
    goal = request.get('goal', 'quality')
    subject_map = {"hero_shot": "product", "model_shot": "human", "flatlay": "product", "ugc": "human", "lifestyle": "human", "detail": "product", "creative_combine": "product"}
    goal_mood_map = {"luxury": "elegant premium luxurious sophisticated", "quality": "refined crafted detailed professional", "versatility": "practical everyday flexible", "gift": "special celebratory warm inviting", "practical": "functional efficient smart"}
    return {"subject_type": subject_map.get(content_type, "product"), "industry": brand.get('industry', ''), "mood": goal_mood_map.get(goal, 'professional'), "keywords": f"{content_type.replace('_', ' ')} {request.get('product_description', '')}".strip()}

def parse_request_with_llm(brand: dict, campaign: dict, request: dict, api_key: str = None) -> dict:
    """用 LLM 理解意图生成搜索 Query"""
    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    prompt = f"""Analyze this content request and generate a search query.
BRAND: {brand.get('name', '')} ({brand.get('industry', '')}) - {', '.join(brand.get('key_selling_points', []))}
TARGET: {brand.get('target_customer', '')}
CAMPAIGN: {campaign.get('theme', '')} - {campaign.get('batch_goal', '')}
REQUEST: {request.get('content_type', '')} for {request.get('product_description', '')}, goal: {request.get('goal', '')}
Return ONLY JSON: {{"subject_type": "human/product/food", "industry": "keywords", "mood": "keywords", "color_tone": "warm/cool/null", "lighting": "soft/natural/studio/null", "keywords": "search terms"}}"""
    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=200)
    try: return json.loads(response.choices[0].message.content.strip().replace("```json", "").replace("```", ""))
    except: return parse_request_to_query(brand, campaign, request)

def compose_fal_prompt(matched_prompts: list, brand: dict, request: dict, api_key: str = None) -> str:
    """合成最终 FAL Prompt"""
    if not matched_prompts: return ""
    base_prompt = prompt_to_fal_text(matched_prompts[0])
    if api_key or os.getenv("OPENAI_API_KEY"):
        client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        enhance = f"""Enhance this prompt for {brand.get('industry', 'lifestyle')} brand.
BASE: {base_prompt}
BRAND: {brand.get('name', '')} - {', '.join(brand.get('key_selling_points', []))}
TARGET: {brand.get('target_customer', '')}
REQUEST: {request.get('content_type', '')} for {request.get('product_description', '')}, goal: {request.get('goal', '')}
Output ONLY enhanced prompt text."""
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": enhance}], temperature=0.5, max_tokens=400)
        return response.choices[0].message.content.strip()
    return base_prompt

def generate_prompt(brand: dict, campaign: dict, request: dict, use_llm: bool = True, api_key: str = None, top_k: int = 3, debug: bool = False) -> dict:
    """主入口: 生成完整的 FAL prompt"""
    query = parse_request_with_llm(brand, campaign, request, api_key) if use_llm and (api_key or os.getenv("OPENAI_API_KEY")) else parse_request_to_query(brand, campaign, request)
    matched = search_prompts(subject_type=query.get('subject_type'), industry=query.get('industry'), mood=query.get('mood'), color_tone=query.get('color_tone'), lighting=query.get('lighting'), keywords=query.get('keywords'), top_k=top_k)
    fal_prompt = compose_fal_prompt(matched, brand, request, api_key)
    result = {"fal_prompt": fal_prompt, "style_reference": {"cluster_id": matched[0].get('cluster_id') if matched else None, "reference_images": [m['image_url'] for m in matched[:3]], "style_summary": matched[0]['prompt'].get('image_style', '')[:100] if matched else ""}}
    if debug: result.update({"search_query": query, "matched_prompts": [{"score": m.get('score', 0), "image_style": m['prompt'].get('image_style', ''), "mood": m['prompt'].get('mood_keywords', [])} for m in matched]})
    return result
