#!/usr/bin/env python3
"""Style Service: 完整的 Prompt 生成服务 (可 copy 到 mcp-content-gen)"""
import json, os, sys
from pathlib import Path
from typing import Optional
from openai import OpenAI
sys.path.insert(0, str(Path(__file__).parent.parent))
from api.prompt_search import search_prompts, prompt_to_fal_text, load_prompts

# === INPUT SCHEMA (你需要传给我的) ===
INPUT_SCHEMA = {
    "brand": {
        "name": "str",
        "industry": "str - fashion/beauty/food/wellness/tech/lifestyle",
        "key_selling_points": ["list of str"],
        "target_customer": "str"
    },
    "campaign": {
        "theme": "str - campaign 主题",
        "batch_goal": "str - 这个 batch 的目标 (可选)"
    },
    "request": {
        "content_type": "str - hero_shot/model_shot/flatlay/ugc/lifestyle/detail/creative_combine",
        "product_description": "str - 产品描述",
        "goal": "str - 想要突出什么 (luxury/quality/versatility/gift/practical)"
    }
}

# === OUTPUT SCHEMA (我返回给你的) ===
OUTPUT_SCHEMA = {
    "fal_prompt": "str - 直接可传给 FAL.ai 的 prompt",
    "style_reference": {
        "cluster_id": "int - 匹配的风格 cluster",
        "reference_images": ["list of image URLs - 风格参考图"],
        "style_summary": "str - 风格摘要"
    },
    "matched_prompts": ["list - Top 3 匹配的 V3 prompts (可选，用于调试)"],
    "search_query": "dict - 生成的搜索 query (可选，用于调试)"
}

def parse_request_to_query(brand: dict, campaign: dict, request: dict) -> dict:
    """Step 1: 解析请求生成搜索 Query (规则版，无需 LLM)"""
    content_type = request.get('content_type', 'hero_shot')
    goal = request.get('goal', 'quality')
    
    # 映射 content_type → subject_type
    subject_map = {"hero_shot": "product", "model_shot": "human", "flatlay": "product", "ugc": "human", "lifestyle": "human", "detail": "product", "creative_combine": "product"}
    
    # 映射 goal → mood keywords
    goal_mood_map = {"luxury": "elegant premium luxurious sophisticated", "quality": "refined crafted detailed professional", "versatility": "practical everyday flexible", "gift": "special celebratory warm inviting", "practical": "functional efficient smart"}
    
    return {
        "subject_type": subject_map.get(content_type, "product"),
        "industry": brand.get('industry', ''),
        "mood": goal_mood_map.get(goal, 'professional'),
        "keywords": f"{content_type.replace('_', ' ')} {request.get('product_description', '')}".strip()
    }

def parse_request_with_llm(brand: dict, campaign: dict, request: dict, api_key: str = None) -> dict:
    """Step 1 (LLM 版): 用 LLM 理解意图生成搜索 Query"""
    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""Analyze this content request and generate a search query for finding matching style prompts.

BRAND CONTEXT:
- Name: {brand.get('name', '')}
- Industry: {brand.get('industry', '')}
- Selling Points: {', '.join(brand.get('key_selling_points', []))}
- Target Customer: {brand.get('target_customer', '')}

CAMPAIGN: {campaign.get('theme', '')}
BATCH GOAL: {campaign.get('batch_goal', '')}

REQUEST:
- Content Type: {request.get('content_type', '')}
- Product: {request.get('product_description', '')}
- Goal: {request.get('goal', '')}

Return ONLY a JSON object with these fields:
{{
    "subject_type": "human" or "product" or "food",
    "industry": "industry keywords for matching intended_use",
    "mood": "mood keywords space-separated (e.g., elegant warm premium)",
    "color_tone": "warm" or "cool" or null,
    "lighting": "soft" or "natural" or "studio" or null,
    "keywords": "additional search keywords"
}}"""

    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=200)
    try:
        return json.loads(response.choices[0].message.content.strip().replace("```json", "").replace("```", ""))
    except:
        return parse_request_to_query(brand, campaign, request)  # Fallback

def compose_fal_prompt(matched_prompts: list, brand: dict, request: dict, api_key: str = None) -> str:
    """Step 3: 合成最终 FAL Prompt"""
    if not matched_prompts: return ""
    
    # 取最佳匹配的 prompt 作为基础
    best = matched_prompts[0]
    base_prompt = prompt_to_fal_text(best)
    
    # 如果有 API key，用 LLM 优化
    if api_key or os.getenv("OPENAI_API_KEY"):
        client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        enhance_prompt = f"""Enhance this image generation prompt for a {brand.get('industry', 'lifestyle')} brand.

BASE PROMPT (from style reference):
{base_prompt}

BRAND CONTEXT:
- Brand: {brand.get('name', '')}
- Selling Points: {', '.join(brand.get('key_selling_points', []))}
- Target Customer: {brand.get('target_customer', '')}

CONTENT REQUEST:
- Type: {request.get('content_type', '')}
- Product: {request.get('product_description', '')}
- Goal: {request.get('goal', '')}

TASK: Combine the style reference with the brand context. Keep the lighting, color, and mood from the base prompt, but adapt the subject to match the product description. Output ONLY the enhanced prompt text, no explanation."""

        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": enhance_prompt}], temperature=0.5, max_tokens=400)
        return response.choices[0].message.content.strip()
    
    return base_prompt

def generate_prompt(brand: dict, campaign: dict, request: dict, use_llm: bool = True, api_key: str = None, top_k: int = 3, debug: bool = False) -> dict:
    """主入口: 生成完整的 FAL prompt"""
    # Step 1: 解析请求生成 Query
    if use_llm and (api_key or os.getenv("OPENAI_API_KEY")):
        query = parse_request_with_llm(brand, campaign, request, api_key)
    else:
        query = parse_request_to_query(brand, campaign, request)
    
    # Step 2: 搜索匹配的 prompts
    matched = search_prompts(subject_type=query.get('subject_type'), industry=query.get('industry'), mood=query.get('mood'), color_tone=query.get('color_tone'), lighting=query.get('lighting'), keywords=query.get('keywords'), top_k=top_k)
    
    # Step 3: 合成最终 prompt
    fal_prompt = compose_fal_prompt(matched, brand, request, api_key)
    
    # 构建输出
    result = {
        "fal_prompt": fal_prompt,
        "style_reference": {
            "cluster_id": matched[0].get('cluster_id') if matched else None,
            "reference_images": [m['image_url'] for m in matched[:3]],
            "style_summary": matched[0]['prompt'].get('image_style', '')[:100] if matched else ""
        }
    }
    
    if debug:
        result["search_query"] = query
        result["matched_prompts"] = [{"score": m.get('score', 0), "image_style": m['prompt'].get('image_style', ''), "mood": m['prompt'].get('mood_keywords', []), "intended_use": m['prompt'].get('intended_use', '')} for m in matched]
    
    return result

# === EXAMPLE USAGE ===
if __name__ == "__main__":
    # 模拟输入
    example_input = {
        "brand": {
            "name": "璃月织锦",
            "industry": "fashion",
            "key_selling_points": ["手工刺绣", "传统工艺", "高端材质"],
            "target_customer": "25-35岁女性, 注重生活品质"
        },
        "campaign": {
            "theme": "2024 春季新品发布",
            "batch_goal": "Day 1: 制造期待感，展示产品高级质感"
        },
        "request": {
            "content_type": "hero_shot",
            "product_description": "silk embroidered handbag with bamboo handle",
            "goal": "luxury"
        }
    }
    
    print("=" * 60)
    print("INPUT:")
    print(json.dumps(example_input, indent=2, ensure_ascii=False))
    
    # 不用 LLM 的版本（纯规则匹配）
    result = generate_prompt(example_input['brand'], example_input['campaign'], example_input['request'], use_llm=False, debug=True)
    
    print("\n" + "=" * 60)
    print("OUTPUT:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
