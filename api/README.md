# 🎨 Style Service API

> 给我品牌信息 + 内容需求，我返回高质量的 FAL.ai prompt + 风格参考图。

## 📥 INPUT

```python
{
    "brand": {
        "name": "品牌名",
        "industry": "fashion | beauty | food | wellness | tech",
        "key_selling_points": ["卖点1", "卖点2"],
        "target_customer": "目标客户描述"
    },
    "campaign": {
        "theme": "活动主题",
        "batch_goal": "这个 batch 的目标"
    },
    "request": {
        "content_type": "hero_shot | model_shot | flatlay | ugc | lifestyle",
        "product_description": "产品描述",
        "goal": "luxury | quality | versatility | gift | practical"
    }
}
```

## 📤 OUTPUT

```python
{
    "fal_prompt": "直接传给 FAL.ai 的 prompt",
    "style_reference": {
        "cluster_id": 79,
        "reference_images": ["url1", "url2", "url3"],
        "style_summary": "风格摘要"
    }
}
```

## 🚀 使用

```python
from api.style_service import generate_prompt

result = generate_prompt(
    brand={"name": "...", "industry": "fashion", ...},
    campaign={"theme": "...", "batch_goal": "..."},
    request={"content_type": "hero_shot", "product_description": "...", "goal": "luxury"},
    use_llm=True  # 需要 OPENAI_API_KEY
)

fal_prompt = result["fal_prompt"]
```
