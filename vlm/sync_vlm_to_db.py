#!/usr/bin/env python3
"""Sync VLM V3 prompts to Supabase - adds vlm_prompt JSONB column"""
import json, sys
from pathlib import Path
from tqdm import tqdm
sys.path.insert(0, str(Path(__file__).parent.parent))
from vector_db.supabase_client import get_client

VLM_RESULTS = Path(__file__).parent.parent / "output" / "vlm_results_v3.json"

def load_vlm_results() -> list[dict]:
    with open(VLM_RESULTS) as f: return [r for r in json.load(f) if r.get('status') == 'success']

def sync_to_db(batch_size: int = 50) -> tuple[int, int]:
    results = load_vlm_results()
    print(f"📊 Loaded {len(results)} VLM results")
    client, success, failed = get_client(), 0, 0
    for i in tqdm(range(0, len(results), batch_size), desc="Syncing"):
        batch = results[i:i + batch_size]
        updates = [{"content_hash": r["content_hash"], "vlm_prompt": r["result"]} for r in batch]
        try:
            client.table("image_embeddings").upsert(updates, on_conflict="content_hash").execute()
            success += len(batch)
        except Exception as e:
            print(f"\n⚠️ Batch {i//batch_size} failed: {e}")
            failed += len(batch)
    return success, failed

if __name__ == "__main__":
    print("🚀 Syncing VLM V3 prompts to Supabase...")
    print("\n⚠️  Make sure you've added the vlm_prompt column:")
    print("    ALTER TABLE image_embeddings ADD COLUMN IF NOT EXISTS vlm_prompt JSONB;\n")
    input("Press Enter to continue or Ctrl+C to cancel...")
    success, failed = sync_to_db()
    print(f"\n✅ Done: {success} synced, {failed} failed")
