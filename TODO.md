# 📋 Style Universe - Project TODO

**Last Updated:** 2024-11-29  
**Current Phase:** Phase 1 Complete → Phase 2 Ready to Start

---

## ✅ Phase 1: Complete

- [x] Pinterest scraper (89k images, 48 categories)
- [x] OpenCLIP embedding pipeline (80,813 embedded)
- [x] Supabase pgvector storage
- [x] K-means clustering (K=120)
- [x] UMAP visualization
- [x] REST API (FastAPI)
- [x] Test frontend (localhost:8000)

---

## 🚀 Phase 2: VLM 风格理解系统 ✅ IMPLEMENTED

### 资源 (已配置)

- [x] **Q-Align**: 本地 M3 Max (免费)
- [x] **Qwen3-VL-8B**: Stanford Cluster endpoint (免费)
- [x] **成本**: $0 🎉

---

### Task 1: VLM 模块基础结构 (Day 1)

- [ ] 创建 `vlm/` 目录结构
- [ ] `vlm/config_vlm.py` - API keys, model settings
- [ ] `vlm/prompts.py` - 三个 prompt 模板 (style/scoring/tagging)
- [ ] `vlm/vlm_client.py` - API 调用封装 (retry + JSON repair)
- [ ] 测试单张图片 VLM 调用

---

### Task 2: 代表图批处理 (Day 2-3)

- [ ] `vlm/run_representatives.py` - 主批处理脚本
- [ ] 从 `clusters.json` 抽取每 cluster 的 5-10 张代表图
- [ ] 对每张图调用 3 个 prompt (style/scoring/tagging)
- [ ] JSON 校验 + 重试机制
- [ ] 结果缓存 (避免重复调用)
- [ ] 进度日志 + 断点续传

**MVP 验证:**
- [ ] 先跑 10 个 cluster (50 张图) 验证质量
- [ ] 检查 JSON 解析成功率 (目标 >95%)
- [ ] 人工检查风格描述质量

---

### Task 3: Cluster-level 聚合 (Day 4)

- [ ] `vlm/aggregate.py` - 聚合代表图结果
- [ ] 合并逻辑:
  - keywords: 频率最高的 10 个
  - color_palette: 频率最高的 3 个
  - scores: 所有代表图的平均值
  - scene_type/subject_type: 最常出现的
- [ ] 输出 `output/cluster_meta.json`

---

### Task 4: 数据库写入 (Day 4-5)

- [ ] Supabase 创建 `cluster_meta` 表:
```sql
CREATE TABLE cluster_meta (
    cluster_id INTEGER PRIMARY KEY,
    style_summary TEXT,
    keywords TEXT[],
    color_palette TEXT[],
    lighting TEXT,
    composition TEXT,
    aesthetic_score FLOAT,
    commercial_score FLOAT,
    ugc_feel FLOAT,
    professional_feel FLOAT,
    scene_type TEXT,
    subject_type TEXT,
    emotion TEXT,
    use_case TEXT[],
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```
- [ ] `vlm/write_supabase.py` - 批量写入脚本
- [ ] 验证数据库数据完整性

---

### Task 5: API 扩展 (Day 5-6)

- [ ] 新增 `GET /clusters/{cluster_id}/meta` 端点
- [ ] 搜索结果附带 cluster_meta
- [ ] 支持按 `commercial_score` / `aesthetic_score` 排序
- [ ] 更新 API 文档

---

### Task 6: 前端更新 (Day 6-7)

- [ ] 显示 cluster 的 style_summary
- [ ] 显示 keywords 标签
- [ ] 显示评分 (aesthetic/commercial)
- [ ] 显示 recommended use cases
- [ ] 颜色调色板可视化

---

## 📝 Notes

### VLM Prompts (参考)

**Style Summary:**
```
You are a senior advertising art director.
Return ONLY a valid JSON:
{
  "style_summary": "1-2 sentences",
  "keywords": ["8-12 keywords"],
  "color_palette": ["3-5 colors"],
  "lighting": "short phrase",
  "composition": "short phrase"
}
```

**Scoring:**
```
Return ONLY a JSON:
{
  "aesthetic_score": float (1-10),
  "commercial_score": float (1-10),
  "composition_score": float (1-10),
  "ugc_feel": float (1-10),
  "professional_feel": float (1-10),
  "issues": ["up to 3 issues"]
}
```

**Tagging:**
```
Return ONLY a JSON:
{
  "scene_type": one of ["studio", "outdoor_nature", "outdoor_urban", "indoor_home", "indoor_store", "other"],
  "subject_type": one of ["product_only", "person_only", "person_with_product", "environment", "other"],
  "emotion": "short phrase",
  "use_case": ["up to 3 marketing use cases"]
}
```

---

### 成本估算

| 模型 | 每张图成本 | 1200张总成本 |
|------|-----------|-------------|
| Claude 3.5 Sonnet | ~$0.04-0.08 | ~$50-100 |
| GPT-4V | ~$0.15-0.30 | ~$180-360 |

---

### 文件结构 (Phase 2 完成后)

```
social-media-style/
├── api/                    # REST API
├── clustering/             # K-means
├── embedding/              # OpenCLIP
├── vector_db/              # Supabase client
├── vlm/                    # 🆕 Phase 2
│   ├── config_vlm.py
│   ├── prompts.py
│   ├── vlm_client.py
│   ├── run_representatives.py
│   ├── aggregate.py
│   └── write_supabase.py
└── output/
    ├── clusters.json
    └── cluster_meta.json   # 🆕 Phase 2
```

---

## 🎯 Done Definition

Phase 2 完成标准:
- [ ] 120 个 cluster 都有 cluster_meta
- [ ] API 能返回 style summary + scores
- [ ] 前端能显示风格信息
- [ ] JSON 解析错误率 < 5%
- [ ] 数据已写入 Supabase

---

## 📞 Quick Commands

```bash
# 启动 API 服务器
cd /Users/haoyangpang/Desktop/Canlah+Marketing/social-media-style
source venv/bin/activate
uvicorn api.main:app --reload --port 8000

# 测试 API
curl http://localhost:8000/health
curl http://localhost:8000/stats
curl -X POST http://localhost:8000/search/text \
  -H "Content-Type: application/json" \
  -d '{"query": "warm cozy valentines", "k": 10}'
```

---

**回来继续时，告诉我 "继续 Phase 2" 我就帮你实现！** 🚀

