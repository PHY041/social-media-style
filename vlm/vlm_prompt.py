#!/usr/bin/env python3
"""VLM Prompt for Style Analysis - based on vlm_output_schema.json v2.0"""

STYLE_ANALYSIS_PROMPT = """You are an expert visual analyst specializing in commercial photography and advertising aesthetics.

Analyze this image and return a JSON object with the following structure. Be specific and detailed in your descriptions.

IMPORTANT: 
- Return ONLY valid JSON, no markdown code blocks, no explanation
- Follow the exact field names and structure below
- For descriptions, write naturally and capture unique details

{
  "product": {
    "category_l1": "fashion|beauty|home|electronics|food|lifestyle|other|none",
    "category_l2": "specific subcategory if applicable",
    "category_l3": "detailed product type if applicable", 
    "material": "main material if visible",
    "price_tier": "luxury|premium|mid_range|budget",
    "target_demographic": "female|male|unisex|kids|all"
  },
  
  "composition": {
    "camera_angle": "flat_lay|eye_level|low_angle|overhead|45_degree|three_quarter",
    "subject_position": "center|rule_of_thirds|corner|scattered|floating",
    "negative_space": "minimal|moderate|generous",
    "framing": "tight_crop|medium|wide|environmental"
  },
  
  "lighting": {
    "type": "soft_diffused|hard_shadow|natural|studio|golden_hour|dramatic|flat|rim",
    "direction": "front|side|back|overhead|multi_point",
    "shadow": "none|soft|medium|hard",
    "temperature": "warm|cool|neutral"
  },
  
  "color": {
    "dominant_colors": ["2-4 main colors by name"],
    "tone": "warm|cool|neutral|mixed",
    "saturation": "muted|natural|vibrant",
    "contrast": "low|medium|high"
  },
  
  "style": {
    "primary_style": "minimalist|luxury|bohemian|modern|vintage|edgy|romantic|sporty|streetwear|editorial|commercial",
    "cultural_aesthetic": "neo_chinese|japanese|scandinavian|mediterranean|american|korean|none",
    "professional_level": "editorial|commercial|prosumer|ugc"
  },
  
  "commercial": {
    "best_industries": ["2-4 industries this image suits"],
    "best_occasions": ["1-3 occasions or campaigns"],
    "brand_tier_fit": "luxury|premium|mass_market|budget"
  },
  
  "platform_fit": {
    "instagram_feed": 0.0-1.0,
    "instagram_story": 0.0-1.0,
    "pinterest": 0.0-1.0,
    "xiaohongshu": 0.0-1.0,
    "tiktok_cover": 0.0-1.0,
    "ecommerce": 0.0-1.0,
    "paid_ads": 0.0-1.0
  },
  
  "text_safe_zones": {
    "has_existing_text": true|false,
    "safe_zones": ["top", "bottom", "left", "right", "center"],
    "logo_placement_viable": true|false
  },
  
  "searchable_tags": {
    "tags": ["10-15 searchable tags covering style, color, product, mood"]
  },
  
  "descriptions": {
    "composition_desc": "2-3 sentences describing the layout, angles, and spatial arrangement",
    "lighting_desc": "1-2 sentences about light quality, direction, and shadow characteristics",
    "color_mood_desc": "2-3 sentences about color palette and emotional atmosphere",
    "style_desc": "2-3 sentences about the overall aesthetic and what makes it distinctive",
    "unique_elements": "1-2 sentences about what makes this specific image stand out"
  },
  
  "generated_prompt": {
    "prompt_en": "A complete prompt in English following this order: TYPE of SUBJECT, COMPOSITION, BACKGROUND, LIGHTING, COLOR/MOOD, STYLE, QUALITY BOOSTERS (8K, sharp focus, etc.)",
    "negative_prompt": "comma-separated list of things to avoid"
  }
}

Remember: Be specific, capture the unique visual qualities, and write prompts that could recreate this style."""


# Shorter version for batch processing (faster, less tokens)
STYLE_ANALYSIS_PROMPT_COMPACT = """Analyze this image as a commercial photography expert. Return ONLY valid JSON:

{
  "product": {"category_l1": "fashion|beauty|home|electronics|food|lifestyle|other|none", "material": "main material", "price_tier": "luxury|premium|mid_range|budget"},
  "composition": {"camera_angle": "flat_lay|eye_level|low_angle|overhead|45_degree", "subject_position": "center|rule_of_thirds|corner|scattered", "negative_space": "minimal|moderate|generous"},
  "lighting": {"type": "soft_diffused|hard_shadow|natural|studio|dramatic", "temperature": "warm|cool|neutral"},
  "color": {"dominant_colors": ["2-4 colors"], "tone": "warm|cool|neutral", "saturation": "muted|natural|vibrant"},
  "style": {"primary_style": "minimalist|luxury|bohemian|modern|vintage|edgy|editorial|commercial", "cultural_aesthetic": "neo_chinese|japanese|scandinavian|none", "professional_level": "editorial|commercial|prosumer|ugc"},
  "commercial": {"best_industries": ["2-3 industries"], "brand_tier_fit": "luxury|premium|mass_market"},
  "platform_fit": {"instagram_feed": 0.0-1.0, "pinterest": 0.0-1.0, "ecommerce": 0.0-1.0, "paid_ads": 0.0-1.0},
  "searchable_tags": {"tags": ["8-12 searchable tags"]},
  "descriptions": {
    "style_summary": "2-3 sentences describing the visual style and mood",
    "unique_elements": "1 sentence about what makes this image special"
  },
  "generated_prompt": {
    "prompt_en": "Complete prompt: TYPE of SUBJECT, COMPOSITION, BACKGROUND, LIGHTING, STYLE, 8K detailed",
    "negative_prompt": "things to avoid"
  }
}"""


if __name__ == "__main__":
    print("Full prompt length:", len(STYLE_ANALYSIS_PROMPT), "chars")
    print("Compact prompt length:", len(STYLE_ANALYSIS_PROMPT_COMPACT), "chars")

