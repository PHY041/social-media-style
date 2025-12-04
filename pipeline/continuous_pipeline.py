#!/usr/bin/env python3
"""Continuous Pipeline: Detect new images → Embed → Q-Align → Cluster
Run as daemon or cron job to process new scraped images automatically
"""
import json, sys, time
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

from vector_db.supabase_client import get_client

OUTPUT_DIR = Path(__file__).parent.parent / "output"
PIPELINE_LOG = OUTPUT_DIR / "pipeline.log"
PROCESSED_HASHES_FILE = OUTPUT_DIR / "processed_hashes.json"

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(PIPELINE_LOG, "a") as f: f.write(f"[{ts}] {msg}\n")

def load_processed_hashes() -> set:
    """Load set of already processed content hashes"""
    if PROCESSED_HASHES_FILE.exists():
        with open(PROCESSED_HASHES_FILE) as f:
            return set(json.load(f))
    return set()

def save_processed_hashes(hashes: set):
    """Save processed hashes"""
    with open(PROCESSED_HASHES_FILE, "w") as f:
        json.dump(list(hashes), f)

def find_new_images_from_scrapers() -> list[dict]:
    """Find new images from scraper output files that aren't in DB yet"""
    new_images = []
    processed = load_processed_hashes()
    
    # Check all scraper output files
    scraper_files = [
        OUTPUT_DIR / "behance_dataset.json",
        OUTPUT_DIR / "dribbble_dataset.json", 
        OUTPUT_DIR / "adsoftheworld_dataset.json",
    ]
    
    for file in scraper_files:
        if not file.exists():
            continue
        
        try:
            with open(file) as f:
                data = json.load(f)
            
            for item in data:
                hash_ = item.get("content_hash")
                if hash_ and hash_ not in processed:
                    new_images.append(item)
                    
        except Exception as e:
            log(f"⚠️ Error reading {file}: {e}")
    
    return new_images

def embed_new_images(images: list[dict]) -> int:
    """Embed new images and upload to Supabase"""
    if not images:
        return 0
    
    log(f"🔄 Embedding {len(images)} new images...")
    
    try:
        # Import embedding pipeline
        from embedding.embed_pipeline import process_batch_streaming
        from embedding.config_embed import BATCH_SIZE
        
        success = 0
        for i in range(0, len(images), BATCH_SIZE):
            batch = images[i:i + BATCH_SIZE]
            # Convert to format expected by embed_pipeline
            batch_data = [{
                "url": img["url"],
                "content_hash": img["content_hash"],
                "category": img.get("search_term", img.get("category", "unknown")),
                "category_type": img.get("category_type", "unknown"),
                "search_term": img.get("search_term", ""),
                "title": img.get("title", ""),
                "alt_text": img.get("alt_text", "")
            } for img in batch]
            
            try:
                result = process_batch_streaming(batch_data)
                success += result
            except Exception as e:
                log(f"   ⚠️ Batch error: {e}")
        
        log(f"   ✅ Embedded {success} images")
        return success
        
    except ImportError as e:
        log(f"   ❌ Import error: {e}")
        return 0

def qalign_new_images(limit: int = 100) -> int:
    """Run Q-Align on images without scores"""
    log(f"🔄 Running Q-Align on unscored images...")
    
    try:
        client = get_client()
        
        # Find images without Q-Align scores
        result = client.table("image_embeddings").select(
            "content_hash,image_url"
        ).is_("qalign_aesthetic", "null").limit(limit).execute()
        
        if not result.data:
            log("   ✅ No unscored images")
            return 0
        
        log(f"   Found {len(result.data)} unscored images")
        
        # Import and run Q-Align
        from vlm.qalign_scorer import score_images, load_qalign
        
        urls = [r["image_url"] for r in result.data]
        hashes = [r["content_hash"] for r in result.data]
        
        scores = score_images(urls, hashes)
        
        # Upload scores
        success = 0
        for score in scores:
            if score.get("qalign_aesthetic") is not None:
                try:
                    client.table("image_embeddings").update({
                        "qalign_aesthetic": score["qalign_aesthetic"],
                        "qalign_quality": score.get("qalign_quality")
                    }).eq("content_hash", score["content_hash"]).execute()
                    success += 1
                except:
                    pass
        
        log(f"   ✅ Scored {success} images")
        return success
        
    except Exception as e:
        log(f"   ❌ Error: {e}")
        return 0

def run_pipeline_once(embed: bool = True, qalign: bool = True, qalign_limit: int = 100):
    """Run one iteration of the pipeline"""
    log("=" * 50)
    log("🚀 Pipeline iteration starting...")
    
    processed = load_processed_hashes()
    
    if embed:
        # Find and embed new images
        new_images = find_new_images_from_scrapers()
        if new_images:
            log(f"📥 Found {len(new_images)} new images from scrapers")
            embedded = embed_new_images(new_images)
            
            # Mark as processed
            for img in new_images:
                processed.add(img["content_hash"])
            save_processed_hashes(processed)
        else:
            log("📥 No new images from scrapers")
    
    if qalign:
        # Run Q-Align on unscored images
        qalign_new_images(limit=qalign_limit)
    
    log("✅ Pipeline iteration complete")
    log("=" * 50)

def run_daemon(interval_minutes: int = 30, embed: bool = True, qalign: bool = True):
    """Run pipeline continuously as a daemon"""
    log(f"🔄 Starting pipeline daemon (interval: {interval_minutes} min)")
    
    while True:
        try:
            run_pipeline_once(embed=embed, qalign=qalign)
        except Exception as e:
            log(f"❌ Pipeline error: {e}")
        
        log(f"💤 Sleeping for {interval_minutes} minutes...")
        time.sleep(interval_minutes * 60)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Continuous pipeline for new images")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=30, help="Daemon interval in minutes")
    parser.add_argument("--no-embed", action="store_true", help="Skip embedding")
    parser.add_argument("--no-qalign", action="store_true", help="Skip Q-Align")
    parser.add_argument("--qalign-limit", type=int, default=100, help="Max images to Q-Align per iteration")
    args = parser.parse_args()
    
    if args.once:
        run_pipeline_once(
            embed=not args.no_embed, 
            qalign=not args.no_qalign,
            qalign_limit=args.qalign_limit
        )
    else:
        run_daemon(
            interval_minutes=args.interval,
            embed=not args.no_embed,
            qalign=not args.no_qalign
        )

if __name__ == "__main__":
    main()



