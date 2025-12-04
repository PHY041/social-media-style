#!/usr/bin/env python3
"""Sync Q-Align scores from JSON to Supabase (can run while qalign_scorer is running)"""
import json, sys
from pathlib import Path
from tqdm import tqdm
sys.path.insert(0, str(Path(__file__).parent.parent))
from vlm.config_vlm import QALIGN_SCORES_JSON
from vector_db.supabase_client import get_client

def sync_scores_to_supabase(batch_size: int = 100):
    """Sync Q-Align scores from JSON file to Supabase"""
    if not QALIGN_SCORES_JSON.exists():
        print(f"❌ No scores file found: {QALIGN_SCORES_JSON}")
        return
    with open(QALIGN_SCORES_JSON) as f: scores = json.load(f)
    valid = [s for s in scores if s.get("qalign_aesthetic") is not None]
    print(f"📤 Syncing {len(valid)} Q-Align scores to Supabase...")
    client = get_client()
    success, failed, skipped = 0, 0, 0
    for i in tqdm(range(0, len(valid), batch_size), desc="Syncing"):
        batch = valid[i:i + batch_size]
        for score in batch:
            try:
                client.table("image_embeddings").update({
                    "qalign_aesthetic": score["qalign_aesthetic"],
                    "qalign_quality": score.get("qalign_quality")
                }).eq("content_hash", score["content_hash"]).execute()
                success += 1
            except Exception as e:
                failed += 1
    print(f"\n✅ Sync complete!")
    print(f"   Success: {success}")
    print(f"   Failed: {failed}")

def check_db_scores():
    """Check how many scores are already in the database"""
    client = get_client()
    result = client.table("image_embeddings").select("content_hash", count="exact").not_.is_("qalign_aesthetic", "null").execute()
    print(f"📊 Database has {result.count} images with Q-Align scores")
    return result.count

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync Q-Align scores to Supabase")
    parser.add_argument("--check", action="store_true", help="Check current DB status")
    parser.add_argument("--sync", action="store_true", help="Sync scores to DB")
    args = parser.parse_args()
    if args.check: check_db_scores()
    elif args.sync: sync_scores_to_supabase()
    else:
        check_db_scores()
        print("\n💡 Run with --sync to upload scores to database")

if __name__ == "__main__": main()



