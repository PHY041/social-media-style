# Style Universe - Visual Intelligence System

Multi-source image scraping (Pinterest, Behance, Dribbble, AdsOfWorld) + AI-powered visual style analysis.

---

## 📁 Project Structure

```
├── settings.py              # 🆕 Unified config (single source of truth)
├── master_scraper.py        # Pinterest scraper entry point
├── scrapers/                # 🆕 All scrapers consolidated
│   ├── behance_scraper.py   # Behance design scraper
│   ├── dribbble_scraper.py  # Dribbble design scraper
│   ├── adsoftheworld_scraper.py  # Ads of World scraper
│   ├── pin_explorer.py      # Pinterest exploration logic
│   └── merge_sources.py     # Merge all sources to master CSV
├── embedding/               # Embedding pipeline
│   ├── config_embed.py      # Config (imports from settings.py)
│   └── embed_pipeline.py    # Download → embed → upload
├── vlm/                     # 🆕 VLM Quality Analysis (Q-Align)
│   ├── qalign_scorer.py     # Smart batch scoring with auto-adjustment
│   ├── laion_aesthetic.py   # Fast LAION aesthetic (alternative)
│   ├── vlm_client.py        # Qwen3-VL Stanford client
│   └── sync_scores_to_db.py # Sync scores to Supabase
├── clustering/              # Clustering & visualization
│   ├── kmeans_cluster.py    # K-means with representatives
│   └── visualize_umap.py    # UMAP 2D/3D + plots
├── api/                     # REST API (FastAPI)
│   ├── main.py              # API entry point
│   └── routers/             # Endpoints
├── vector_db/               # Supabase pgvector
│   └── supabase_client.py   # CRUD + similarity search
└── output/
    ├── master_dataset.csv   # 140k+ images (all sources)
    ├── qalign_scores.json   # Q-Align aesthetic/quality scores
    └── clusters.json        # Cluster data
```

---

## 🚀 Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set Supabase credentials
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

### 2. Scrape Images

```bash
# Start Chrome with remote debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Run Pinterest scraper (uses expanded 76 categories)
python master_scraper.py

# Or run other scrapers (use port 9223 for second Chrome instance)
python -m scrapers.behance_scraper
python -m scrapers.dribbble_scraper
python -m scrapers.adsoftheworld_scraper
```

### 3. Merge & Embed

```bash
# Merge all sources into master CSV
python -c "from scrapers.merge_sources import merge_all_sources; merge_all_sources()"

# Generate embeddings (uploads to Supabase)
python -m embedding.embed_pipeline --resume
```

### 4. Q-Align Quality Scoring

```bash
# Smart scoring with dynamic batch (adjusts based on CPU/memory)
python -m vlm.qalign_scorer

# Features:
# - Starts with batch=32, auto-reduces if system stressed
# - Resumes from checkpoint
# - Saves every 20 batches
```

### 5. Run API

```bash
uvicorn api.main:app --reload --port 8000
# Open http://localhost:8000
```

---

## 📊 Data Sources

| Source | Images | Status |
|--------|--------|--------|
| Pinterest | ~112k | ✅ Active |
| Behance | ~20k | ✅ Active |
| Dribbble | ~3.5k | ✅ Active |
| AdsOfWorld | ~4k | ✅ Active |
| **Total** | **~140k** | |

---

## 🧠 Q-Align Quality Scoring

Q-Align is a 7B VLM that scores images on:
- **Aesthetic Score** (1-5): Visual appeal
- **Quality Score** (1-5): Technical quality

**Score Distribution (52k images):**
```
0.0-2.0:  2% (filter out)
2.0-2.5:  6% (low quality)
2.5-3.0: 18% (acceptable)
3.0-3.5: 33% (good)
3.5-4.0: 30% (very good)
4.0-5.0: 12% (excellent)
```

**Threshold:** `>= 2.5` keeps 92% of images

---

## 🔧 Configuration

All settings in `settings.py`:

| Setting | Value | Description |
|---------|-------|-------------|
| `CLIP_MODEL` | `ViT-L-14` | OpenCLIP model |
| `EMBED_DIM` | 768 | Embedding dimension |
| `QALIGN_BATCH_SIZE` | 16 | Q-Align batch (for 48GB M3 Max) |
| `DEFAULT_K` | 120 | Cluster count |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/search/text` | Text-to-image search |
| `GET` | `/clusters` | List all clusters |
| `GET` | `/clusters/{id}` | Cluster details |

**Example:**
```bash
curl -X POST http://localhost:8000/search/text \
  -H "Content-Type: application/json" \
  -d '{"query": "minimalist luxury product photography", "k": 20}'
```

---

## 📈 Pipeline

```
Scrape → Merge → Embed → Q-Align → Cluster → API
  ↓        ↓       ↓        ↓         ↓       ↓
Pinterest  CSV   Supabase  Scores   K=120   REST
Behance           pgvector  JSON            
Dribbble                                     
AdsOfWorld                                   
```

---

## ⚠️ Notes

- **Smart Q-Align:** Auto-adjusts batch size based on CPU/memory
- **No local images:** Streaming pipeline saves disk space
- **M3 Max optimized:** Uses MPS (Metal) for GPU acceleration
- **Unified config:** All settings in `settings.py`
