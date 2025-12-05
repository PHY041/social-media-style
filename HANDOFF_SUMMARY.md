# 项目交接文档 - Style Universe

> 最后更新: 2025-12-05
> 
> GitHub: https://github.com/PHY041/social-media-style

---

## 📋 项目概述

**Style Universe** 是一个视觉风格智能分析系统，用于：
- 从 Pinterest/Behance/Dribbble 等平台收集高质量商业图片
- 使用 AI 进行风格分析和分类
- 为 AI 图片生成提供可复用的 Prompt

---

## ✅ 已完成的工作

### Phase 1: 数据收集与嵌入

| 任务 | 状态 | 详情 |
|------|------|------|
| **Pinterest 爬虫** | ✅ 完成 | `scrapers/master_scraper.py`, 112k+ 图片 |
| **Behance 爬虫** | ✅ 完成 | `scrapers/behance_scraper.py`, ~20k 图片 |
| **Dribbble 爬虫** | ✅ 完成 | `scrapers/dribbble_scraper.py`, ~3.5k 图片 |
| **AdsOfWorld 爬虫** | ✅ 完成 | `scrapers/adsoftheworld_scraper.py`, ~4.3k 图片 |
| **数据合并去重** | ✅ 完成 | `output/master_dataset.csv`, 140k+ 图片 |
| **OpenCLIP Embedding** | ✅ 完成 | ViT-L-14, 768-dim, 存入 Supabase |
| **Supabase pgvector** | ✅ 完成 | 109,694 张图片已嵌入 |

### Phase 2: 质量过滤

| 任务 | 状态 | 详情 |
|------|------|------|
| **Q-Align 评分** | ✅ 完成 | `vlm/qalign_scorer.py`, 109,694 张已评分 |
| **质量过滤** | ✅ 完成 | aesthetic >= 2.5, 95,528 张高质量图 |
| **分数同步到 Supabase** | ✅ 完成 | `qalign_aesthetic`, `qalign_quality` 字段 |

### Phase 3: 聚类分析

| 任务 | 状态 | 详情 |
|------|------|------|
| **K-Means 聚类** | ✅ 完成 | K=150, 基于高质量图片 |
| **代表图提取** | ✅ 完成 | 每 cluster 5 张, 共 750 张 |
| **Cluster 保存** | ✅ 完成 | `output/clusters.json` |

### Phase 4: VLM 风格分析 (进行中)

| 任务 | 状态 | 详情 |
|------|------|------|
| **VLM Schema 设计** | ✅ 完成 | `vlm/vlm_output_schema.json` |
| **Prompt 写作指南** | ✅ 完成 | `vlm/prompt_writing_guide.json` |
| **Stanford Qwen3-VL 集成** | ✅ 完成 | `vlm/vlm_client.py` |
| **测试验证** | ✅ 完成 | 3 张测试图, 效果良好 |
| **批量处理 750 张** | 🔄 进行中 | `vlm/run_vlm_batch.py`, ~5小时 |

---

## 📁 关键文件结构

```
social-media-style/
├── settings.py              # 统一配置文件
├── output/
│   ├── master_dataset.csv   # 主数据集 (140k+ 图片)
│   ├── clusters.json        # 150 个 cluster
│   ├── qalign_scores.json   # Q-Align 评分
│   └── vlm_results.json     # VLM 分析结果 (生成中)
├── scrapers/                # 各平台爬虫
├── embedding/               # OpenCLIP 嵌入
├── clustering/              # K-Means 聚类
├── vlm/
│   ├── vlm_output_schema.json   # VLM 输出结构定义
│   ├── prompt_writing_guide.json # Prompt 写作指南
│   ├── vlm_prompt.py            # VLM 分析 Prompt
│   ├── vlm_client.py            # Stanford API 客户端
│   ├── run_vlm_batch.py         # 批量处理脚本
│   └── qalign_scorer.py         # Q-Align 评分器
├── vector_db/               # Supabase 客户端
├── api/                     # FastAPI 服务 (待完善)
└── prompt_learning/         # 1,648 个 Prompt-Image Pairs
```

---

## 📊 当前数据统计

| 指标 | 数值 |
|------|------|
| **总收集图片** | 140,141 |
| **Supabase 嵌入** | 109,694 |
| **高质量图片 (>=2.5)** | 95,528 |
| **Clusters** | 150 |
| **代表图** | 750 |
| **VLM 已处理** | ~进行中 |

---

## 🔧 关键配置

### Supabase
- 表: `image_embeddings`
- 字段: `content_hash`, `embedding`, `image_url`, `category`, `qalign_aesthetic`, `qalign_quality`, `cluster_id`

### Stanford VLM Endpoint
```
URL: http://myth60.stanford.edu:9821/v1
Model: Qwen/Qwen3-VL-8B-Instruct
API Key: 49bea0181c25e0808f7f000ff157bc76
```
> ⚠️ 注意: Stanford 服务可能会被抢占，需要联系 Dhruba 重启

### Q-Align
- Model: `q-future/one-align`
- Device: MPS (M3 Max)
- Threshold: aesthetic >= 2.5

---

## 🚀 未来改进方向

### 1. VLM Prompt 优化 (高优先级)

**问题**: 当前 Prompt 生成的细节不够丰富

**改进方向**:
- 参考 Gemini 的层级结构，增加空间关系描述
- 添加更详细的材质、纹理描述
- 增加中文 Prompt 支持
- 添加艺术家/风格参考 (如 "in the style of Alphonse Mucha")

**示例改进结构**:
```json
{
  "spatial_layout": {
    "foreground": "...",
    "midground": "...",
    "background": "...",
    "left_side": "...",
    "right_side": "..."
  },
  "materials_textures": ["布艺", "厚涂", "木质"],
  "detailed_colors": ["铁锈红", "橄榄绿", "鼠尾草绿"]
}
```

### 2. Prompt-Image Pairs 利用

**现有资源**: `prompt_learning/` 下有 1,648 对 Prompt-Image

**待做**:
- 用 VLM 分析这些图片，建立 "视觉属性 ↔ Prompt 词汇" 映射
- 学习哪些 Prompt 词汇能产生哪些视觉效果
- 构建 Prompt 词库，用于生成更精准的 Prompt

### 3. 扩展代表图数量

**当前**: 5 张/cluster = 750 张
**建议**: 10 张/cluster = 1,500 张

修改 `settings.py`:
```python
CLUSTER_REPRESENTATIVES = 10
```

然后重新运行 clustering。

### 4. API 服务完善

`api/` 目录下有基础的 FastAPI 框架，需要:
- 完善 `/search/text` 端点
- 添加 VLM 分析结果到响应
- 实现 Style DNA 聚合

### 5. Style DNA 生成

**目标**: 为每个 Cluster 生成风格摘要

**步骤**:
1. VLM 分析完 750 张代表图
2. 聚合每个 cluster 的 VLM 输出
3. 生成 cluster 级别的 "Style DNA"
4. 存入 `output/cluster_meta.json`

---

## ⚠️ 注意事项

1. **Stanford VLM 不稳定**: 服务会被抢占，需要联系 Dhruba Ghosh 重启
2. **Supabase 超时**: 大查询可能超时，已实现分页处理
3. **Q-Align 内存占用**: 建议 batch_size=32，动态调整
4. **Pinterest 登录**: 爬虫需要手动登录 Chrome (debug port 9222)

---

## 📞 相关联系人

- **Stanford VLM**: Dhruba Ghosh
- **项目 Owner**: Haoyang Pang

---

## 🔄 当前正在运行的任务

```bash
# VLM 批量分析 (750 张, ~5小时)
nohup python -m vlm.run_vlm_batch > output/vlm_batch.log 2>&1 &

# 检查进度
tail -f output/vlm_batch.log
```

---

## 📝 快速命令参考

```bash
# 激活环境
cd /Users/haoyangpang/Desktop/Canlah+Marketing/social-media-style
source venv/bin/activate

# 检查 VLM 进度
python3 -c "import json; d=json.load(open('output/vlm_results.json')); print(f'完成: {len(d)}/750')"

# 重新 Clustering
python -m clustering.kmeans_cluster --k 150 --min-aesthetic 2.5

# 测试 Stanford VLM
curl http://myth60.stanford.edu:9821/v1/models -H "Authorization: Bearer 49bea0181c25e0808f7f000ff157bc76"

# 运行 API 服务
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

*文档生成时间: 2025-12-05*

