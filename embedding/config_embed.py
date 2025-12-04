#!/usr/bin/env python3
"""Embedding Config - imports from unified settings.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings import (  # Re-export from unified settings
    PROJECT_ROOT, OUTPUT_DIR, MASTER_CSV, CLUSTERS_JSON, VISUALIZATIONS_DIR,
    CLIP_MODEL as MODEL_NAME, CLIP_PRETRAINED as PRETRAINED, EMBED_DIM,
    EMBED_BATCH_SIZE as BATCH_SIZE, MAX_CONCURRENT_DOWNLOADS, DOWNLOAD_TIMEOUT,
    get_text_weight, DEFAULT_K, K_CANDIDATES, CLUSTER_REPRESENTATIVES, SUPABASE_TABLE
)

# Backwards compatibility
RETRY_ATTEMPTS = 3
IMAGE_SIZE = 224
EMBEDDINGS_PARQUET = OUTPUT_DIR / "embeddings.parquet"
UMAP_OUTPUT_DIR = VISUALIZATIONS_DIR
