#!/usr/bin/env python3
"""Unified settings for Style Universe - consolidates all config"""
from pathlib import Path

# === PATHS ===
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
MASTER_CSV = OUTPUT_DIR / "master_dataset.csv"
CLUSTERS_JSON = OUTPUT_DIR / "clusters.json"
VISUALIZATIONS_DIR = OUTPUT_DIR / "visualizations"

# === BROWSER (Scrapers) ===
CHROME_DEBUG_PORT = 9222
CHROME_DEBUG_PORT_2 = 9223  # Second instance for Behance/Dribbble

# === SCRAPER SETTINGS ===
DELAY_BETWEEN_PAGES = (2, 3)
DELAY_BETWEEN_SCROLLS = (0.2, 0.4)
COOLDOWN_EVERY_N_PINS = 25
COOLDOWN_DURATION = (15, 30)
PINS_PER_SEARCH = 30
SCROLLS_PER_PIN = 50
MAX_URLS_PER_PIN = 100
DUPLICATE_STOP_THRESHOLD = 0.76

# === EMBEDDING MODEL ===
CLIP_MODEL = "ViT-L-14"
CLIP_PRETRAINED = "laion2b_s32b_b82k"
EMBED_DIM = 768
EMBED_BATCH_SIZE = 64
MAX_CONCURRENT_DOWNLOADS = 16
DOWNLOAD_TIMEOUT = 30
def get_text_weight(title: str, alt_text: str) -> float: # Dynamic weight
    if title and alt_text: return 0.30
    if alt_text or title: return 0.15
    return 0.05

# === CLUSTERING ===
DEFAULT_K = 120
K_CANDIDATES = [80, 120, 160]
CLUSTER_REPRESENTATIVES = 10

# === Q-ALIGN (VLM) ===
QALIGN_MODEL = "q-future/one-align"
QALIGN_MIN_SCORE = 2.5
QALIGN_BATCH_SIZE = 16  # For 48GB M3 Max
QALIGN_DEVICE = "mps"
QALIGN_SCORES_JSON = OUTPUT_DIR / "qalign_scores.json"

# === QWEN3-VL (Stanford) ===
STANFORD_ENDPOINT = "http://myth60.stanford.edu:9821/v1"
STANFORD_API_KEY = "49bea0181c25e0808f7f000ff157bc76"
STANFORD_MODEL = "Qwen/Qwen3-VL-8B-Instruct"
VLM_MAX_TOKENS = 2000
VLM_TEMPERATURE = 0.3

# === VLM OUTPUTS ===
VLM_RESULTS_JSON = OUTPUT_DIR / "vlm_results.json"
PROMPT_DNA_JSON = OUTPUT_DIR / "prompt_dna.json"
CLUSTER_META_JSON = OUTPUT_DIR / "cluster_meta.json"

# === CLUSTER FILTERING ===
TOP_K_PER_CLUSTER = 10
MIN_IMAGES_PER_CLUSTER = 3

# === SUPABASE ===
SUPABASE_TABLE = "image_embeddings"

# === CSV COLUMNS ===
CSV_COLUMNS = ["url", "pin_url", "category", "category_type", "search_term", "title", "alt_text", "saves", "comments", "engagement_score", "content_hash", "collected_at", "source"]

# === VLM PROMPTS ===
STYLE_PROMPT = """You are a senior advertising art director analyzing high-quality commercial photography.
Look at the image and return ONLY a valid JSON object (no markdown, no explanation):
{
  "style_summary": "2-3 sentences describing the professional advertising visual style",
  "keywords": ["10-15 advertising/marketing style keywords"],
  "color_palette": ["4-6 main colors with descriptive names"],
  "lighting": "detailed lighting description",
  "composition": "composition and framing description",
  "mood": "emotional tone and atmosphere",
  "commercial_use": ["3-5 specific commercial use cases"],
  "generation_prompt": "A detailed prompt suitable for AI image generation to recreate this style"
}"""

SCORING_PROMPT = """You are an expert commercial photography evaluator.
Rate this professional image and return ONLY a valid JSON object:
{
  "commercial_score": float 1-10 (how effective for advertising),
  "brand_fit": float 1-10 (how suitable for premium brands),
  "attention_grabbing": float 1-10 (scroll-stopping power),
  "production_quality": float 1-10 (professional execution),
  "strengths": ["2-3 key strengths"],
  "style_category": "one of: minimal, luxury, bold, warm, editorial, lifestyle, studio, outdoor"
}"""

