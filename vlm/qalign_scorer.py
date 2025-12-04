#!/usr/bin/env python3
"""Smart Q-Align scorer with dynamic batch sizing based on system resources"""
import json, torch, asyncio, aiohttp, sys, psutil, time
from PIL import Image
from io import BytesIO
from tqdm import tqdm
from pathlib import Path
import warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent.parent))
from vlm.config_vlm import QALIGN_MODEL, QALIGN_DEVICE, QALIGN_SCORES_JSON, QALIGN_MIN_SCORE
from vector_db.supabase_client import get_client

MAX_BATCH = 32  # Start aggressive
MIN_BATCH = 4   # Minimum safe batch
DOWNLOAD_CONCURRENCY = 30
CHECKPOINT_EVERY = 20
MEMORY_THRESHOLD = 85  # Reduce batch if memory > 85%
CPU_THRESHOLD = 95     # Reduce batch if CPU > 95%

_model = None

def get_system_stats() -> dict: # Get CPU and memory usage
    return {"cpu": psutil.cpu_percent(interval=0.1), "memory": psutil.virtual_memory().percent}

def load_qalign():
    global _model
    if _model is None:
        print(f"🔄 Loading Q-Align on {QALIGN_DEVICE}...")
        from transformers import AutoModelForCausalLM
        _model = AutoModelForCausalLM.from_pretrained(QALIGN_MODEL, trust_remote_code=True, attn_implementation="eager", torch_dtype=torch.float16, low_cpu_mem_usage=True)
        _model = _model.to(QALIGN_DEVICE).eval()
        print("✅ Q-Align loaded")
    return _model

async def download_image_async(session: aiohttp.ClientSession, url: str) -> tuple[str, Image.Image | None]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200: return url, Image.open(BytesIO(await resp.read())).convert("RGB")
    except: pass
    return url, None

async def download_batch_async(urls: list[str]) -> dict[str, Image.Image | None]:
    connector = aiohttp.TCPConnector(limit=DOWNLOAD_CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector, headers={"User-Agent": "Mozilla/5.0"}) as session:
        return {url: img for url, img in await asyncio.gather(*[download_image_async(session, url) for url in urls])}

def score_batch(model, images: list[Image.Image]) -> tuple[list[float], list[float]]:
    if not images: return [], []
    try:
        aesthetics = model.score(images, task_="aesthetics", input_="image")
        qualities = model.score(images, task_="quality", input_="image")
        def to_list(x, n):  # Convert tensor/list to list of floats
            if isinstance(x, torch.Tensor):
                if x.dim() == 0: return [float(x.item())] * n  # Scalar tensor
                return [float(v.item()) for v in x.flatten()]  # Multi-element tensor
            if hasattr(x, '__iter__'): return [float(v.item()) if hasattr(v, 'item') else float(v) for v in x]
            return [float(x)] * n  # Single value
        a_list = to_list(aesthetics, len(images))
        q_list = to_list(qualities, len(images))
        return a_list, q_list
    except Exception as e:
        print(f"⚠️ Batch error: {e}")
        return [None] * len(images), [None] * len(images)

def fetch_images(limit: int = None) -> list[dict]:
    print("📂 Fetching images from Supabase...")
    all_data, offset = [], 0
    while True:
        result = get_client().table("image_embeddings").select("content_hash,image_url").range(offset, offset + 999).execute()
        if not result.data: break
        all_data.extend(result.data)
        if len(result.data) < 1000 or (limit and len(all_data) >= limit): break
        offset += 1000
    print(f"   Fetched {len(all_data)} images")
    return all_data[:limit] if limit else all_data

def run_smart_scoring(limit: int = None, resume: bool = True):
    images = fetch_images(limit)
    scored = {}
    if resume and QALIGN_SCORES_JSON.exists():
        with open(QALIGN_SCORES_JSON) as f: scored = {r["content_hash"]: r for r in json.load(f)}
        print(f"   Resuming: {len(scored)} already scored")
    
    to_score = [img for img in images if img["content_hash"] not in scored]
    print(f"📊 Smart scoring {len(to_score)} images (adaptive batch: {MIN_BATCH}-{MAX_BATCH})")
    if not to_score: return print("✅ All done!")
    
    model = load_qalign()
    batch_size = MAX_BATCH
    consecutive_success = 0
    pbar = tqdm(total=len(to_score), desc=f"Scoring (batch={batch_size})")
    idx = 0
    
    while idx < len(to_score):
        stats = get_system_stats() # Check system resources
        if stats["memory"] > MEMORY_THRESHOLD or stats["cpu"] > CPU_THRESHOLD:
            old_batch = batch_size
            batch_size = max(MIN_BATCH, batch_size // 2)
            if old_batch != batch_size:
                print(f"\n⚠️ High load (CPU:{stats['cpu']:.0f}% MEM:{stats['memory']:.0f}%), reducing batch: {old_batch} → {batch_size}")
            consecutive_success = 0
            time.sleep(2)  # Cool down
        elif consecutive_success >= 10 and batch_size < MAX_BATCH: # Gradually increase batch if stable
            batch_size = min(MAX_BATCH, batch_size + 4)
            print(f"\n✅ Stable, increasing batch → {batch_size}")
            consecutive_success = 0
        
        batch = to_score[idx:idx + batch_size]
        url_to_img = asyncio.run(download_batch_async([img["image_url"] for img in batch]))
        
        valid_items, valid_imgs = [], []
        for item in batch:
            img = url_to_img.get(item["image_url"])
            if img:
                valid_items.append(item)
                valid_imgs.append(img)
            else:
                scored[item["content_hash"]] = {"content_hash": item["content_hash"], "image_url": item["image_url"], "qalign_aesthetic": None, "qalign_quality": None, "status": "download_failed"}
        
        if valid_imgs:
            try:
                a_scores, q_scores = score_batch(model, valid_imgs)
                for item, a, q in zip(valid_items, a_scores, q_scores):
                    scored[item["content_hash"]] = {"content_hash": item["content_hash"], "image_url": item["image_url"], "qalign_aesthetic": round(a, 3) if a else None, "qalign_quality": round(q, 3) if q else None, "status": "success" if a else "error"}
                consecutive_success += 1
            except Exception as e:
                print(f"\n❌ Batch failed: {e}, reducing batch size")
                batch_size = max(MIN_BATCH, batch_size // 2)
                consecutive_success = 0
                continue  # Retry with smaller batch
        
        idx += len(batch)
        pbar.update(len(batch))
        pbar.set_description(f"Scoring (batch={batch_size}, CPU:{stats['cpu']:.0f}%)")
        
        if (idx // batch_size) % CHECKPOINT_EVERY == 0: # Checkpoint
            with open(QALIGN_SCORES_JSON, "w") as f: json.dump(list(scored.values()), f)
    
    pbar.close()
    with open(QALIGN_SCORES_JSON, "w") as f: json.dump(list(scored.values()), f)
    passed = sum(1 for r in scored.values() if r.get("qalign_aesthetic") and r["qalign_aesthetic"] >= QALIGN_MIN_SCORE)
    print(f"✅ Done! {len(scored)} scored, {passed} passed (>= {QALIGN_MIN_SCORE})")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    run_smart_scoring(limit=args.limit, resume=not args.no_resume)

