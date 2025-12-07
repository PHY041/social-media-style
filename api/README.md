# 🎨 Style Service API

> **TL;DR**: 给我品牌信息 + 内容需求，我返回高质量的 FAL.ai prompt + 风格参考图。

---

## 🎯 这个服务做什么？

基于 **746 个高质量商业图片的 V3 Prompt**，智能匹配并生成适合你品牌的图片生成 prompt。

```
你的品牌 + 内容需求  →  Style Service  →  FAL-ready prompt + 参考图
```

---

## 📦 核心文件

```
api/
├── style_service.py   # 主入口 ⭐
├── prompt_search.py   # 搜索逻辑
└── README.md          # 本文档
```

---

## 📥 INPUT 结构

```python
{
    "brand": {
        "name": "品牌名",
        "industry": "fashion",  # fashion | beauty | food | wellness | tech | lifestyle
        "key_selling_points": ["手工制作", "高端材质", "传统工艺"],
        "target_customer": "25-35岁女性, 注重生活品质"
    },
    "campaign": {
        "theme": "2024 春季新品发布",
        "batch_goal": "Day 1: 制造期待感，展示产品高级质感"  # 可选
    },
    "request": {
        "content_type": "hero_shot",  # 见下方列表
        "product_description": "silk embroidered handbag with bamboo handle",
        "goal": "luxury"  # 见下方列表
    }
}
```

### Content Types

| Type | 说明 | Subject |
|------|------|---------|
| `hero_shot` | 产品主图 | product |
| `model_shot` | 模特展示 | human |
| `flatlay` | 平铺摆拍 | product |
| `ugc` | 用户生成风格 | human |
| `lifestyle` | 生活场景 | human/scene |
| `detail` | 细节特写 | product |
| `creative_combine` | 创意组合 | product |

### Goals

| Goal | 风格倾向 |
|------|----------|
| `luxury` | 优雅、高级、精致 |
| `quality` | 品质感、工艺细节 |
| `versatility` | 日常、实用、百搭 |
| `gift` | 温馨、节日、送礼 |
| `practical` | 功能性、效率 |

---

## 📤 OUTPUT 结构

```python
{
    "fal_prompt": "Studio flat lay featuring luxury beauty products... Lighting: warm soft. Background: clean white surface. Color: warm tones...",
    
    "style_reference": {
        "cluster_id": 79,
        "reference_images": [
            "https://i.pinimg.com/originals/00/67/43/...",
            "https://i.pinimg.com/originals/f6/bf/bc/...",
            "https://i.pinimg.com/originals/4d/81/de/..."
        ],
        "style_summary": "Studio flat lay featuring luxury beauty products with high-end fashion elements"
    },
    
    # debug=True 时返回
    "search_query": { ... },
    "matched_prompts": [ ... ]
}
```

### 字段说明

| 字段 | 说明 | 用途 |
|------|------|------|
| `fal_prompt` | 完整的文本 prompt | 直接传给 FAL.ai |
| `reference_images` | 3 张风格参考图 URL | 展示/未来 i2i |
| `cluster_id` | 匹配的风格 cluster | 调试 |
| `style_summary` | 风格简述 | 展示 |

---

## 🚀 使用方式

### 方式 1: 直接导入 (推荐)

```python
from api.style_service import generate_prompt

result = generate_prompt(
    brand={
        "name": "璃月织锦",
        "industry": "fashion",
        "key_selling_points": ["手工刺绣", "传统工艺"],
        "target_customer": "25-35岁女性"
    },
    campaign={
        "theme": "2024 春季新品",
        "batch_goal": "展示高级质感"
    },
    request={
        "content_type": "hero_shot",
        "product_description": "silk handbag with bamboo handle",
        "goal": "luxury"
    },
    use_llm=True,        # 使用 LLM 增强 (需要 OPENAI_API_KEY)
    debug=True           # 返回调试信息
)

# 直接用于 FAL.ai
fal_prompt = result["fal_prompt"]
```

### 方式 2: 不用 LLM (纯规则匹配)

```python
result = generate_prompt(brand, campaign, request, use_llm=False)
```

---

## 🔧 环境变量

```bash
# 可选：如果要用 LLM 增强 prompt
OPENAI_API_KEY=sk-xxx
```

---

## 📊 数据来源

| 数据 | 数量 | 说明 |
|------|------|------|
| V3 Prompts | 746 | 高质量商业图片的详细描述 |
| 风格 Clusters | 150 | K-Means 聚类 |
| 图片来源 | Pinterest, Behance, Dribbble | 多平台采集 |

---

## 🔍 搜索逻辑

1. **解析请求** → 生成搜索 Query
2. **多字段匹配**:
   - `subject.type` (human/product/food)
   - `intended_use` (fashion/wellness/beauty...)
   - `mood_keywords` (elegant/warm/minimalist...)
   - `lighting.type` (soft/natural/studio)
   - `color_palette.tone` (warm/cool)
3. **评分排序** → 返回 Top K
4. **LLM 合成** → 结合品牌信息生成最终 prompt

---

## 📝 示例输出

**Input**: Fashion brand, luxury handbag, hero shot

**Output `fal_prompt`**:
```
Professional hero shot photography for fashion brand. 
Subject: silk embroidered handbag with bamboo handle. 
Brand positioning: 手工刺绣, 传统工艺, 高端材质. 
Target audience: 25-35岁女性, 注重生活品质. 
Lighting: warm soft studio from front-left. 
Background: clean, minimal, marble texture. 
Composition: centered product as focal point, eye-level angle. 
Color: warm tones with deep matte black, warm beige, natural tones. 
Mood: elegant, premium, sophisticated, serene. 
Focus: sharp on product, subtle background blur.
```

---

## 🤝 集成到 MCP Content Gen

```python
# 在 mcp-content-gen 的 enhance_xxx_prompt() 中:

from style_service import generate_prompt

async def enhance_hero_shot_prompt(brand_context: dict, request: str):
    result = generate_prompt(
        brand=brand_context,
        campaign={"theme": current_campaign_theme},
        request={
            "content_type": "hero_shot",
            "product_description": extract_product_from_request(request),
            "goal": "luxury"
        }
    )
    return result["fal_prompt"]
```

---

## 📞 Questions?

- **Style Service**: @Haoyang
- **MCP Integration**: TBD
