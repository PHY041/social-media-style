#!/usr/bin/env python3
"""Batch VLM analysis on cluster representatives"""
import json
import time
import sys
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from vlm.config_vlm import STANFORD_ENDPOINT, STANFORD_API_KEY, STANFORD_MODEL, VLM_RESULTS_JSON
from vlm.vlm_prompt import STYLE_ANALYSIS_PROMPT

# Config
MAX_TOKENS = 2000
TEMPERATURE = 0.3
CHECKPOINT_EVERY = 10
RETRY_DELAY = 2

def load_clusters():
    clusters_file = Path(__file__).parent.parent / "output" / "clusters.json"
    return json.load(open(clusters_file))

def load_existing_results():
    if VLM_RESULTS_JSON.exists():
        return json.load(open(VLM_RESULTS_JSON))
    return []

def save_results(results):
    VLM_RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(VLM_RESULTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def call_vlm(client, image_url: str, max_retries: int = 3) -> dict | None:
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=STANFORD_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": STYLE_ANALYSIS_PROMPT}
                    ]
                }],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            raw = response.choices[0].message.content.strip()
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"\n   ⚠️ JSON parse error: {e}")
            return None
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"\n   ⚠️ Retry {attempt + 1}/{max_retries}: {e}")
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                print(f"\n   ❌ Failed: {e}")
                return None
    return None

def main():
    print("🚀 VLM Batch Analysis")
    print("=" * 60)
    
    # Load data
    clusters = load_clusters()
    existing = load_existing_results()
    
    # Get all representatives
    all_reps = []
    for cluster in clusters:
        for rep in cluster['representatives']:
            all_reps.append({
                'cluster_id': cluster['cluster_id'],
                'content_hash': rep['content_hash'],
                'image_url': rep['image_url'],
                'category': rep.get('category', 'unknown')
            })
    
    print(f"📊 Total representatives: {len(all_reps)}")
    
    # Check already processed
    processed_hashes = {r['content_hash'] for r in existing if r.get('status') == 'success'}
    to_process = [r for r in all_reps if r['content_hash'] not in processed_hashes]
    
    print(f"✅ Already processed: {len(processed_hashes)}")
    print(f"📋 To process: {len(to_process)}")
    
    if not to_process:
        print("\n🎉 All done!")
        return
    
    # Initialize client
    client = OpenAI(api_key=STANFORD_API_KEY, base_url=STANFORD_ENDPOINT)
    
    # Process
    results = existing.copy()
    success_count = len(processed_hashes)
    fail_count = sum(1 for r in existing if r.get('status') != 'success')
    
    print(f"\n🔄 Starting batch processing...")
    print(f"   Checkpoint every {CHECKPOINT_EVERY} images")
    print("=" * 60)
    
    start_time = time.time()
    
    for i, rep in enumerate(tqdm(to_process, desc="Processing")):
        result = call_vlm(client, rep['image_url'])
        
        record = {
            'cluster_id': rep['cluster_id'],
            'content_hash': rep['content_hash'],
            'image_url': rep['image_url'],
            'category': rep['category'],
            'vlm_output': result,
            'status': 'success' if result else 'failed',
            'processed_at': datetime.now().isoformat()
        }
        results.append(record)
        
        if result:
            success_count += 1
        else:
            fail_count += 1
        
        # Checkpoint
        if (i + 1) % CHECKPOINT_EVERY == 0:
            save_results(results)
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            remaining = (len(to_process) - i - 1) / rate if rate > 0 else 0
            tqdm.write(f"   💾 Checkpoint: {success_count} success, {fail_count} failed | ETA: {remaining/60:.1f} min")
    
    # Final save
    save_results(results)
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"✅ Batch complete!")
    print(f"   Total: {len(results)}")
    print(f"   Success: {success_count}")
    print(f"   Failed: {fail_count}")
    print(f"   Time: {elapsed/60:.1f} minutes")
    print(f"   Saved to: {VLM_RESULTS_JSON}")

if __name__ == "__main__":
    main()

