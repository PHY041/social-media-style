#!/usr/bin/env python3
"""LAION Aesthetic Predictor - 50-100x faster than Q-Align, uses OpenCLIP embeddings"""
import json, torch, asyncio, aiohttp, sys
from PIL import Image
from io import BytesIO
from tqdm import tqdm
from pathlib import Path
import open_clip
import numpy as np
import warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent.parent))

AESTHETIC_MODEL_URL = "https://github.com/LAION-AI/aesthetic-predictor/raw/main/sa_0_4_vit_l_14_linear.pth"
BATCH_SIZE = 64  # Much larger batch than Q-Align!
DOWNLOAD_CONCURRENCY = 50
CHECKPOINT_EVERY = 100
SCORES_JSON = Path(__file__).parent.parent / "output" / "laion_aesthetic_scores.json"

class LAIONAestheticScorer:
    def __init__(self, device: str = "mps"):
        self.device = device
        print(f"🔄 Loading OpenCLIP ViT-L-14 on {device}...")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms("ViT-L-14", pretrained="openai")
        self.model = self.model.to(device).eval()
        print("🔄 Loading LAION aesthetic MLP...")
        self.aesthetic_mlp = self._load_aesthetic_mlp()
        print("✅ LAION Aesthetic loaded")
    
    def _load_aesthetic_mlp(self):  # Load aesthetic predictor head
        import torch.nn as nn
        mlp = nn.Sequential(nn.Linear(768, 1024), nn.Dropout(0.2), nn.Linear(1024, 128), nn.Dropout(0.2), nn.Linear(128, 64), nn.Dropout(0.1), nn.Linear(64, 16), nn.Linear(16, 1)).to(self.device)
        state_dict = torch.hub.load_state_dict_from_url(AESTHETIC_MODEL_URL, map_location=self.device)
        mlp.load_state_dict(state_dict)
        mlp.eval()
        return mlp
    
    @torch.no_grad()
    def score_batch(self, images: list[Image.Image]) -> list[float]:
        if not images: return []
        tensors = torch.stack([self.preprocess(img) for img in images]).to(self.device)
        embeddings = self.model.encode_image(tensors).float()
        embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        scores = self.aesthetic_mlp(embeddings).squeeze(-1).cpu().numpy()
        return [round(float(s), 3) for s in scores]

async def download_image_async(session: aiohttp.ClientSession, url: str) -> tuple[str, Image.Image | None]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
            if resp.status == 200: return url, Image.open(BytesIO(await resp.read())).convert("RGB")
    except: pass
    return url, None

async def download_batch_async(urls: list[str]) -> dict[str, Image.Image | None]:
    connector = aiohttp.TCPConnector(limit=DOWNLOAD_CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector, headers={"User-Agent": "Mozilla/5.0"}) as session:
        return {url: img for url, img in await asyncio.gather(*[download_image_async(session, url) for url in urls])}

def fetch_all_images_from_db(limit: int = None) -> list[dict]:
    from vector_db.supabase_client import get_client
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

def run_laion_scoring(limit: int = None, resume: bool = True):
    images = fetch_all_images_from_db(limit)
    scored = {}
    if resume and SCORES_JSON.exists():
        with open(SCORES_JSON) as f: scored = {r["content_hash"]: r for r in json.load(f)}
        print(f"   Resuming: {len(scored)} already scored")
    
    to_score = [img for img in images if img["content_hash"] not in scored]
    print(f"📊 Scoring {len(to_score)} images (batch={BATCH_SIZE}, 🚀 LAION ~50x faster)")
    if not to_score: return print("✅ All done!")
    
    scorer = LAIONAestheticScorer()
    total_batches = (len(to_score) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for batch_idx in tqdm(range(0, len(to_score), BATCH_SIZE), total=total_batches, desc="LAION Batches"):
        batch = to_score[batch_idx:batch_idx + BATCH_SIZE]
        url_to_img = asyncio.run(download_batch_async([img["image_url"] for img in batch]))
        
        valid_items, valid_imgs = [], []
        for item in batch:
            img = url_to_img.get(item["image_url"])
            if img:
                valid_items.append(item)
                valid_imgs.append(img)
            else:
                scored[item["content_hash"]] = {"content_hash": item["content_hash"], "image_url": item["image_url"], "laion_aesthetic": None, "status": "download_failed"}
        
        if valid_imgs:
            scores = scorer.score_batch(valid_imgs)
            for item, score in zip(valid_items, scores):
                scored[item["content_hash"]] = {"content_hash": item["content_hash"], "image_url": item["image_url"], "laion_aesthetic": score, "status": "success"}
        
        if (batch_idx // BATCH_SIZE + 1) % CHECKPOINT_EVERY == 0:
            with open(SCORES_JSON, "w") as f: json.dump(list(scored.values()), f)
    
    with open(SCORES_JSON, "w") as f: json.dump(list(scored.values()), f)
    passed = sum(1 for r in scored.values() if r.get("laion_aesthetic") and r["laion_aesthetic"] >= 5.0)
    print(f"✅ Done! {len(scored)} scored, {passed} passed (>= 5.0)")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    run_laion_scoring(limit=args.limit, resume=not args.no_resume)

