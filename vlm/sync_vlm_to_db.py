#!/usr/bin/env python3
"""Sync VLM V3 prompts to Supabase - UPDATE existing records only"""
import json, sys
from pathlib import Path
from tqdm import tqdm
sys.path.insert(0, str(Path(__file__).parent.parent))
from vector_db.supabase_client import get_client

VLM_RESULTS = Path(__file__).parent.parent / "output" / "vlm_results_v3.json"

def load_vlm_results() -> list[dict]:
    with open(VLM_RESULTS) as f: return [r for r in json.load(f) if r.get('status') == 'success']

def sync_to_db() -> tuple[int, int]:
    results = load_vlm_results()
    print(f"📊 Loaded {len(results)} VLM results")
    client, success, failed = get_client(), 0, 0
    for r in tqdm(results, desc="Syncing"):
        try:
            client.table("image_embeddings").update({"vlm_prompt": r["result"]}).eq("content_hash", r["content_hash"]).execute()
            success += 1
        except Exception as e:
            print(f"\n⚠️ {r['content_hash'][:8]} failed: {e}")
            failed += 1
    return success, failed

if __name__ == "__main__":
    print("🚀 Syncing VLM V3 prompts to Supabase (UPDATE only)...")
    success, failed = sync_to_db()
    print(f"\n✅ Done: {success} synced, {failed} failed")
