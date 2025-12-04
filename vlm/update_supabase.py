import json, sys # Update Supabase with Q-Align scores and cluster meta
from pathlib import Path
from tqdm import tqdm
sys.path.insert(0, str(Path(__file__).parent.parent))
from vlm.config_vlm import QALIGN_SCORES_JSON, CLUSTER_META_JSON
from vector_db.supabase_client import get_client

def update_qalign_scores_in_db(batch_size: int = 50):
    """Update image_embeddings table with Q-Align scores"""
    if not QALIGN_SCORES_JSON.exists():
        print(f"❌ Run qalign_scorer.py first: {QALIGN_SCORES_JSON}")
        return
    with open(QALIGN_SCORES_JSON) as f: scores = json.load(f)
    valid = [s for s in scores if s.get("qalign_aesthetic") is not None]
    print(f"📤 Updating {len(valid)} Q-Align scores in Supabase...")
    client = get_client()
    success, failed = 0, 0
    for i in tqdm(range(0, len(valid), batch_size), desc="Batches"):
        batch = valid[i:i + batch_size]
        for score in batch:
            try:
                client.table("image_embeddings").update({"qalign_aesthetic": score["qalign_aesthetic"], "qalign_quality": score.get("qalign_quality")}).eq("content_hash", score["content_hash"]).execute()
                success += 1
            except Exception as e:
                failed += 1
    print(f"✅ Updated {success} records, {failed} failed")

def create_cluster_meta_table():
    """SQL to create cluster_meta table (run in Supabase SQL editor)"""
    sql = """
-- Create cluster_meta table for VLM results
CREATE TABLE IF NOT EXISTS cluster_meta (
    cluster_id INTEGER PRIMARY KEY,
    size INTEGER,
    num_hq_images INTEGER,
    avg_qalign FLOAT,
    keywords TEXT[],
    color_palette TEXT[],
    commercial_use TEXT[],
    lighting TEXT,
    composition TEXT,
    mood TEXT,
    style_category TEXT,
    sample_prompts TEXT[],
    avg_commercial_score FLOAT,
    avg_brand_fit FLOAT,
    avg_attention FLOAT,
    avg_production FLOAT,
    base_prompt TEXT,
    style_modifiers TEXT[],
    negative_modifiers TEXT[],
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add Q-Align columns to image_embeddings (if not exists)
ALTER TABLE image_embeddings ADD COLUMN IF NOT EXISTS qalign_aesthetic FLOAT;
ALTER TABLE image_embeddings ADD COLUMN IF NOT EXISTS qalign_quality FLOAT;
"""
    print("📋 Run this SQL in Supabase SQL Editor:\n")
    print(sql)
    return sql

def upload_cluster_meta():
    """Upload cluster_meta.json to Supabase"""
    if not CLUSTER_META_JSON.exists():
        print(f"❌ Run generate_prompt_dna.py first: {CLUSTER_META_JSON}")
        return
    with open(CLUSTER_META_JSON) as f: meta_list = json.load(f)
    print(f"📤 Uploading {len(meta_list)} cluster meta records...")
    client = get_client()
    success, failed = 0, 0
    for meta in tqdm(meta_list, desc="Clusters"):
        try:
            record = {"cluster_id": meta["cluster_id"], "size": meta.get("size"), "num_hq_images": meta.get("num_hq_images"), "avg_qalign": meta.get("avg_qalign"), "keywords": meta.get("keywords"), "color_palette": meta.get("color_palette"), "commercial_use": meta.get("commercial_use"), "lighting": meta.get("lighting"), "composition": meta.get("composition"), "mood": meta.get("mood"), "style_category": meta.get("style_category"), "sample_prompts": meta.get("sample_prompts")}
            if meta.get("avg_scores"):
                record.update({"avg_commercial_score": meta["avg_scores"].get("commercial"), "avg_brand_fit": meta["avg_scores"].get("brand_fit"), "avg_attention": meta["avg_scores"].get("attention"), "avg_production": meta["avg_scores"].get("production")})
            client.table("cluster_meta").upsert(record).execute()
            success += 1
        except Exception as e:
            print(f"   ⚠️ Cluster {meta['cluster_id']} failed: {e}")
            failed += 1
    print(f"✅ Uploaded {success} records, {failed} failed")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Update Supabase with VLM results")
    parser.add_argument("--scores", action="store_true", help="Update Q-Align scores")
    parser.add_argument("--meta", action="store_true", help="Upload cluster meta")
    parser.add_argument("--schema", action="store_true", help="Print SQL schema")
    args = parser.parse_args()
    if args.schema: create_cluster_meta_table()
    elif args.scores: update_qalign_scores_in_db()
    elif args.meta: upload_cluster_meta()
    else: parser.print_help()

if __name__ == "__main__": main()



