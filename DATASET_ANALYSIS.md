# Pinterest Visual Marketing Dataset Analysis

**Generated:** November 25, 2025  
**Dataset:** `master_dataset.csv`

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Image URLs** | 89,112 |
| **Unique Images** | 89,112 (100% unique) |
| **Source Pins Explored** | 4,886 |
| **Categories Covered** | 48 |
| **Category Types** | 5 |
| **Search Terms Used** | 48 |

---

## 🏷️ Category Type Distribution

| Type | Count | % of Total | Description |
|------|-------|------------|-------------|
| **Occasion** | 19,805 | 22.2% | Marketing events (Black Friday, CNY, etc.) |
| **Product** | 19,089 | 21.4% | Product categories (bags, shoes, tech) |
| **Visual** | 18,275 | 20.5% | Photography styles (hero, flatlay, UGC) |
| **Style** | 16,933 | 19.0% | Aesthetic styles (minimalist, bold, warm) |
| **Vertical** | 15,010 | 16.8% | Industry verticals (fitness, travel, art) |

---

## 🔥 Top 15 Categories by Volume

| Rank | Category | Images | Type |
|------|----------|--------|------|
| 1 | `style_warm` | 4,157 | Style |
| 2 | `occasion_school` | 2,174 | Occasion |
| 3 | `style_bold` | 2,161 | Style |
| 4 | `vertical_art` | 2,056 | Vertical |
| 5 | `occasion_valentines` | 2,055 | Occasion |
| 6 | `occasion_halloween` | 2,025 | Occasion |
| 7 | `occasion_cny` | 2,025 | Occasion |
| 8 | `vertical_pet` | 2,020 | Vertical |
| 9 | `style_vintage` | 2,019 | Style |
| 10 | `occasion_newyear` | 2,013 | Occasion |
| 11 | `vertical_outdoor` | 2,012 | Vertical |
| 12 | `vertical_travel` | 1,985 | Vertical |
| 13 | `visual_beforeafter` | 1,978 | Visual |
| 14 | `occasion_blackfriday` | 1,958 | Occasion |
| 15 | `visual_model` | 1,953 | Visual |

---

## 🛍️ Product Categories

| Category | Images | Use Case |
|----------|--------|----------|
| `furniture` | 1,764 | Home & living brands |
| `shoes` | 1,737 | Footwear retailers |
| `home_decor` | 1,712 | Interior design |
| `chinese_fashion` | 1,639 | Asian market fashion |
| `beauty` | 1,625 | Cosmetics & skincare |
| `style_luxury` | 1,621 | Premium brands |
| `tech` | 1,579 | Electronics |
| `fashion` | 1,578 | Apparel |
| `sportswear` | 1,572 | Athletic brands |
| `drinks` | 1,554 | Beverage industry |
| `style_minimalist` | 1,527 | Clean aesthetic brands |
| `luxury_bags` | 1,505 | Designer accessories |
| `food` | 1,503 | F&B industry |
| `jewelry` | 1,321 | Accessories |

---

## 📅 Marketing Occasions Covered

| Occasion | Images | Peak Season |
|----------|--------|-------------|
| `occasion_school` | 2,174 | Aug-Sep |
| `occasion_valentines` | 2,055 | Feb |
| `occasion_halloween` | 2,025 | Oct |
| `occasion_cny` | 2,025 | Jan-Feb |
| `occasion_newyear` | 2,013 | Dec-Jan |
| `occasion_blackfriday` | 1,958 | Nov |
| `occasion_christmas` | 1,943 | Dec |
| `occasion_summer` | 1,935 | Jun-Aug |
| `occasion_singles` | 1,850 | Nov 11 |
| `occasion_mothers` | 1,827 | May |
| `vertical_wedding` | 1,449 | Year-round |

---

## 📸 Visual/Photography Types

| Type | Images | Best For |
|------|--------|----------|
| `visual_beforeafter` | 1,978 | Transformation content |
| `visual_model` | 1,953 | Fashion & lifestyle |
| `visual_social` | 1,927 | Social media posts |
| `visual_bts` | 1,869 | Behind-the-scenes |
| `visual_detail` | 1,833 | Product close-ups |
| `visual_hero` | 1,798 | Hero banners |
| `visual_ugc` | 1,737 | User-generated style |
| `visual_lifestyle` | 1,731 | Contextual shots |
| `visual_flatlay` | 1,730 | Top-down layouts |
| `visual_unboxing` | 1,719 | Unboxing content |

---

## 🎨 Aesthetic Styles

| Style | Images | Mood |
|-------|--------|------|
| `style_warm` | 4,157 | Cozy, inviting |
| `style_bold` | 2,161 | Vibrant, energetic |
| `style_vintage` | 2,019 | Retro, nostalgic |
| `style_dark` | 1,872 | Moody, dramatic |
| `style_natural` | 1,813 | Organic, earthy |
| `style_pastel` | 1,763 | Soft, feminine |
| `style_luxury` | 1,621 | Premium, elegant |
| `style_minimalist` | 1,527 | Clean, simple |

---

## 📋 Data Schema

```csv
url,pin_url,category,category_type,search_term,title,alt_text,saves,comments,engagement_score,content_hash,collected_at
```

| Field | Description |
|-------|-------------|
| `url` | High-resolution image URL (originals) |
| `pin_url` | Source Pinterest pin |
| `category` | Category label |
| `category_type` | product/style/visual/occasion/vertical |
| `search_term` | Search query used |
| `title` | Pin title |
| `alt_text` | Image description |
| `saves` | Save count |
| `comments` | Comment count |
| `engagement_score` | Calculated engagement |
| `content_hash` | Unique content identifier |
| `collected_at` | Timestamp |

---

## ⚠️ Data Completeness Report

| Field | Has Data | Empty/Zero | Fill Rate | Notes |
|-------|----------|------------|-----------|-------|
| `url` | 89,112 | 0 | **100%** ✅ | All images have URLs |
| `pin_url` | 89,112 | 0 | **100%** ✅ | ⚠️ This is **root pin**, not each image's own pin |
| `category` | 89,112 | 0 | **100%** ✅ | All categorized |
| `category_type` | 89,112 | 0 | **100%** ✅ | All typed |
| `search_term` | 89,112 | 0 | **100%** ✅ | All have search term |
| `title` | 38,757 | 50,355 | **43.5%** ⚠️ | Many pins have no title |
| `alt_text` | 75,326 | 13,786 | **84.5%** ✅ | Good coverage |
| `saves` | 0 | 89,112 | **0%** ❌ | Not available from "More like this" |
| `comments` | 0 | 89,112 | **0%** ❌ | Not available from "More like this" |
| `engagement_score` | 0 | 89,112 | **0%** ❌ | Cannot calculate without saves/comments |
| `content_hash` | 89,112 | 0 | **100%** ✅ | Unique identifier |
| `collected_at` | 89,112 | 0 | **100%** ✅ | Timestamp |

### 🔍 Why Engagement Data is Missing

**原因：** Pinterest 的 "More like this" 区域只显示缩略图，不显示 saves/comments。

要获取 engagement 数据，需要单独访问每个 pin 页面，这会：
- 速度慢 10x
- 更容易被 Pinterest 封禁

### 🔍 Why pin_url is Root Pin

**原因：** `pin_url` 存储的是**来源 pin**（我们点进去探索的那个 pin），不是每张图片自己的 pin URL。

- 89,112 张图片来自 4,886 个 root pins
- 平均每个 pin 产出 ~18 张相关图片

---

## 💡 Potential Use Cases

### 1. **AI/ML Training**
- Style transfer models
- Product photography generation
- Marketing content classification
- Visual search systems

### 2. **Marketing Automation**
- Seasonal campaign inspiration
- A/B test visual variants
- Trend analysis
- Competitor benchmarking

### 3. **E-commerce Enhancement**
- Product photography reference
- Lifestyle shot inspiration
- Cross-sell visual matching
- Category-specific styling

### 4. **Content Generation**
- Social media post templates
- Ad creative inspiration
- Email marketing visuals
- Landing page design

---

## 🔧 Technical Notes

- **Resolution:** All URLs point to Pinterest "originals" (highest resolution)
- **Deduplication:** 100% unique images via content hashing
- **Collection Method:** Pin-to-pin exploration (not search-heavy)
- **Anti-blocking:** Random delays, cooldowns, human-like browsing

---

## 📈 Next Steps

1. **Expand Dataset** - Continue to 150K+ images
2. **Add Engagement Data** - Enrich with saves/comments
3. **Quality Scoring** - Rank by visual quality
4. **Clustering** - Group similar visuals
5. **API Integration** - Build retrieval system

---

*Dataset collected using ethical scraping practices respecting Pinterest's guidelines.*

