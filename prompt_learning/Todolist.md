# Nano Banana Pro Prompt 项目 Todolist

> 最后更新: 2025-11-29

---

## ✅ 已完成

### 数据爬取
- [x] OpenNana 爬取 - 610 条 prompt
- [x] GitHub 仓库爬取 - 486 条 prompt
- [x] Youmind 完整爬取 - 523 条 prompt (含图片、作者、日期)
- [x] Feishu 文档手动整理 - 29 条 prompt (含是否需要参考图标注)

### 数据处理
- [x] 统一数据格式 (12个字段)
- [x] 去重处理 (1,656 → 1,648)
- [x] 自动分类 (11个类别)
- [x] 合并到 `all_prompts_merged.json`

### 分析提取
- [x] 提取 Prompt 写作框架/结构
- [x] 生成 `prompt_writing_schema.json` 模板
- [x] 分析常用关键词和字段

---

## 📋 待办事项

### 高优先级
- [ ] **整合到 social-media-style 项目**
  - [ ] 将写作框架导入主项目
  - [ ] 设计 Prompt 生成器模块

- [ ] **审美训练数据准备**
  - [ ] 确定高审美图片来源 (Pinterest/Instagram)
  - [ ] 设计图片筛选标准
  - [ ] 建立审美评分体系

### 中优先级
- [ ] **Prompt 生成器开发**
  - [ ] 输入: 图片类型 + 审美特征
  - [ ] 输出: 结构化的高质量 Prompt
  - [ ] 使用写作框架模板

- [ ] **数据增强**
  - [ ] 爬取更多来源 (Twitter/X 上的优秀 prompt)
  - [ ] 收集官方 Google Gemini 示例
  - [ ] 添加更多分类标签

### 低优先级
- [ ] **图片下载** - 下载 1,138 张示例图片到本地
- [ ] **英文翻译** - 补充缺失的英文 prompt
- [ ] **质量评分** - 为每个 prompt 添加质量评分

---

## 📁 当前文件结构

```
/prompt-scraper/
├── output/
│   ├── all_prompts_merged.json    # ⭐ 主数据文件 (1,648条)
│   ├── all_prompts_merged.csv     # CSV格式
│   ├── prompt_writing_schema.json # ⭐ 写作框架模板
│   ├── opennana_prompts.json      # 原始数据
│   ├── github_prompts.json
│   ├── youmind_prompts_full.json
│   ├── feishu_prompts_manual.json
│   └── feishu_prompts_summary.md
├── scrape_opennana.py
├── scrape_github.py
├── scrape_youmind_v2.py
├── merge_and_classify.py
├── config.py
└── Todolist.md                    # 本文件
```

---

## 📊 数据统计

| 指标 | 数值 |
|------|------|
| 总 Prompts | 1,648 |
| 有图片 | 1,138 (69%) |
| 有英文 | 1,015 (61%) |
| 需要参考图 | 17 |

### 来源分布
- OpenNana: 610 (37%)
- Youmind: 523 (32%)
- GitHub: 486 (29%)
- Feishu: 29 (2%)

### 分类分布
- 其他: 463
- 人物/肖像: 279
- 风景/场景: 207
- 设计/UI: 189
- 艺术/插画: 156
- 摄影/编辑: 100
- 文字/排版: 86
- 3D/产品: 64
- 创意/超现实: 46
- 教育/信息图: 37
- 动物: 21

---

## 💡 核心洞察

**这些 Prompt 的价值:**
- ✅ 学习 "写什么" - 该描述哪些元素
- ✅ 学习 "怎么写" - 结构化描述方式
- ✅ 学习 "用什么词" - 专业术语

**审美需要另外训练:**
- 用你自己的高质量图片训练"什么是好看"
- Prompt 结构只告诉你"怎么描述"

---

## 🔗 相关项目

- `social-media-style/` - 主项目 (embedding + clustering)
- 可以将此 prompt 数据整合进去

---

*有问题随时继续*



