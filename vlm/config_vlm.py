#!/usr/bin/env python3
"""VLM Config - imports from unified settings.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings import (  # Re-export from unified settings
    OUTPUT_DIR, CLUSTERS_JSON, QALIGN_SCORES_JSON, VLM_RESULTS_JSON, PROMPT_DNA_JSON, CLUSTER_META_JSON,
    QALIGN_MODEL, QALIGN_MIN_SCORE, QALIGN_BATCH_SIZE, QALIGN_DEVICE,
    STANFORD_ENDPOINT, STANFORD_API_KEY, STANFORD_MODEL, VLM_MAX_TOKENS, VLM_TEMPERATURE,
    TOP_K_PER_CLUSTER, MIN_IMAGES_PER_CLUSTER, STYLE_PROMPT, SCORING_PROMPT
)

# Backwards compatibility
PROJECT_ROOT = Path(__file__).parent.parent
