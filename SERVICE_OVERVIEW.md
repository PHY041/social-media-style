# 🎨 Social Media Style DNA Service

> **TL;DR**: 给我一张图，我返回一个结构化的 JSON prompt，可直接用于 AI 图像生成。

---

## 🎯 这个服务是做什么的？

我们建立了一个 **视觉风格数据库**，包含：
- **109,694 张** 高质量社交媒体图片（Pinterest, Behance, Dribbble, Ads of the World）
- **95,528 张** 通过 Q-Align 美学评分筛选的图片
- **150 个风格聚类**，每个聚类 5 张代表图
- **746 个** 详细的 V3 Prompt（JSON 格式）

---

## 📦 数据结构

### Supabase `image_embeddings` 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `content_hash` | TEXT (PK) | 图片唯一标识 |
| `image_url` | TEXT | 图片 URL |
| `embedding` | VECTOR(768) | OpenCLIP 向量 |
| `cluster_id` | INTEGER | 风格聚类 ID (0-149) |
| `qalign_aesthetic` | FLOAT | 美学评分 (0-5) |
| `vlm_prompt` | JSONB | **V3 Prompt** ⭐ |

---

## 🔥 V3 Prompt 结构

```json
{
  "image_style": "Studio flat lay photograph featuring...",
  "canvas": {
    "aspect_ratio": "1:1",
    "orientation": "square"
  },
  "scene": {
    "subject": {
      "type": "human | product | food | animal | object | scene",
      "description": "自然语言描述",
      "details": {
        // 根据 type 动态字段
        // human: skin_texture, cropping, pose, expression, clothing, hair
        // product: material, shape, arrangement
      }
    },
    "environment": { "setting", "background", "surface", "props" },
    "lighting": { "type", "direction", "quality", "shadow" }
  },
  "composition": { "framing", "camera_angle", "focus", "subject_position" },
  "color_palette": {
    "dominant": ["warm peach", "soft orange"],  // 自然语言，无 HEX
    "accents": ["white"],
    "tone": "warm",
    "mood": "playful, cozy"
  },
  "typography": { "has_text", "text_content", "font_style" },
  "mood_keywords": ["serene", "minimalist", "natural"],
  "intended_use": "product photography, social media content"
}
```

---

## 🚀 如何使用

### 1️⃣ 按风格搜索
```python
from vector_db.supabase_client import search_similar

# 给定一张图的 embedding，找相似风格
results = search_similar(my_embedding, limit=10)
```

### 2️⃣ 按聚类获取 Prompt
```python
# 获取某个风格聚类的所有 prompt
from supabase import create_client
client = create_client(url, key)
prompts = client.table("image_embeddings") \
    .select("vlm_prompt") \
    .eq("cluster_id", 42) \
    .not_.is_("vlm_prompt", "null") \
    .execute()
```

### 3️⃣ 直接用 Prompt 生成图
```python
# V3 Prompt 可直接作为 AI 图像生成的输入
prompt = results[0]["vlm_prompt"]
# 发送到 DALL-E / Midjourney / Stable Diffusion
```

---

## 📊 当前状态

| 阶段 | 任务 | 状态 |
|------|------|------|
| **Phase 1** | 数据收集 + Embedding | ✅ 109,694 张 |
| **Phase 2** | Q-Align 美学评分 | ✅ 95,528 张 |
| **Phase 3** | K-Means 聚类 | ✅ 150 clusters |
| **Phase 4** | VLM Prompt 生成 | ✅ 746/750 |
| **Phase 5** | 同步到 Supabase | ⏳ 待执行 |

---

## 🔧 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 填写 SUPABASE_URL, SUPABASE_ANON_KEY

# 3. 运行 VLM 批处理（需要 Ollama）
ollama pull qwen3-vl:8b
python vlm/run_vlm_simple.py

# 4. 同步到数据库
python vlm/sync_vlm_to_db.py
```

---

## 📁 关键文件

```
vlm/
├── vlm_output_schema_v3.json  # Prompt 结构定义
├── run_vlm_simple.py          # Ollama 批处理
├── run_vlm_batch.py           # Stanford 批处理
├── vlm_client.py              # Stanford API 客户端
└── qalign_scorer.py           # Q-Align 评分

output/
├── vlm_results_v3.json        # 746 个 V3 Prompts
└── clusters.json              # 150 个聚类

vector_db/
└── supabase_client.py         # 数据库操作
```

---

## 👥 联系

- **VLM/Prompt 相关**: 找我
- **Stanford GPU**: 联系 Dhruba（会被抢占，需要重启）
- **Supabase**: 管理员权限找 [TBD]

---

## 🔮 下一步

1. **集成到 MCP Content Gen** — 使用 `api/style_service.py`

---

## 🔗 API 服务 (已完成)

详见 `api/README.md`

```python
from api.style_service import generate_prompt

result = generate_prompt(
    brand={"name": "...", "industry": "fashion", ...},
    campaign={"theme": "...", "batch_goal": "..."},
    request={"content_type": "hero_shot", "product_description": "...", "goal": "luxury"}
)

fal_prompt = result["fal_prompt"]
reference_images = result["style_reference"]["reference_images"]
```

