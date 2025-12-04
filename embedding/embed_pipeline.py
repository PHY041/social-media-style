import asyncio, aiohttp, csv, io, sys, time # Streaming embedding pipeline: download → embed → upload → delete
from PIL import Image
import torch
import open_clip
import numpy as np
from tqdm import tqdm
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from embedding.config_embed import *
from vector_db.supabase_client import upsert_batch

class EmbeddingPipeline:
    def __init__(self):
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"  # M3 Max Metal
        print(f"🖥️ Using device: {self.device}")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=PRETRAINED)
        self.model = self.model.to(self.device).eval()
        self.tokenizer = open_clip.get_tokenizer(MODEL_NAME)
        print(f"✅ Loaded {MODEL_NAME}/{PRETRAINED}")

    def _build_text(self, row: dict) -> str:  # Combine text fields
        parts = [row.get("title", ""), row.get("alt_text", ""), row.get("category", ""), row.get("search_term", "")]
        return " | ".join(p for p in parts if p)

    @torch.no_grad()
    def _embed_batch(self, images: list[Image.Image], texts: list[str], weights: list[float]) -> np.ndarray:  # Batch embed images + texts with dynamic fusion
        img_tensors = torch.stack([self.preprocess(img) for img in images]).to(self.device)
        img_embs = self.model.encode_image(img_tensors).float().cpu().numpy()
        img_embs = img_embs / np.linalg.norm(img_embs, axis=1, keepdims=True)
        
        text_tokens = self.tokenizer(texts).to(self.device)
        txt_embs = self.model.encode_text(text_tokens).float().cpu().numpy()
        txt_embs = txt_embs / np.linalg.norm(txt_embs, axis=1, keepdims=True)
        
        weights = np.array(weights).reshape(-1, 1)
        fused = (1.0 * img_embs + weights * txt_embs)
        return fused / np.linalg.norm(fused, axis=1, keepdims=True)  # L2 normalize

    async def _download_image(self, session: aiohttp.ClientSession, url: str) -> Image.Image | None:  # Download single image
        for _ in range(RETRY_ATTEMPTS):
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return Image.open(io.BytesIO(data)).convert("RGB")
            except: pass
        return None

    async def _process_batch(self, session: aiohttp.ClientSession, batch: list[dict]) -> list[dict]:  # Process a batch: download → embed → prepare records
        tasks = [self._download_image(session, row["url"]) for row in batch]
        images = await asyncio.gather(*tasks)
        
        valid_rows, valid_imgs, texts, weights = [], [], [], []
        for row, img in zip(batch, images):
            if img is None: continue
            valid_rows.append(row)
            valid_imgs.append(img)
            texts.append(self._build_text(row))
            weights.append(get_text_weight(row.get("title", ""), row.get("alt_text", "")))
        
        if not valid_imgs: return []
        embeddings = self._embed_batch(valid_imgs, texts, weights)
        
        records = []
        for row, emb in zip(valid_rows, embeddings):
            records.append({
                "content_hash": row["content_hash"], "image_url": row["url"],
                "category": row["category"], "category_type": row["category_type"],
                "search_term": row["search_term"], "title": row.get("title", ""),
                "alt_text": row.get("alt_text", ""), "embedding": emb.tolist()
            })
        return records

    def load_csv(self) -> list[dict]:  # Load master dataset
        with open(MASTER_CSV, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    async def run(self, limit: int = None, skip_existing: set[str] = None):  # Main pipeline
        rows = self.load_csv()
        if limit: rows = rows[:limit]
        if skip_existing: rows = [r for r in rows if r["content_hash"] not in skip_existing]
        
        print(f"📊 Processing {len(rows)} images in batches of {BATCH_SIZE}")
        total_uploaded, failed = 0, 0
        
        connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_DOWNLOADS)
        async with aiohttp.ClientSession(connector=connector) as session:
            for i in tqdm(range(0, len(rows), BATCH_SIZE), desc="Batches"):
                batch = rows[i:i + BATCH_SIZE]
                records = await self._process_batch(session, batch)
                if records:
                    success = upsert_batch(records)
                    total_uploaded += success
                    failed += len(records) - success
                await asyncio.sleep(0.1)  # Rate limit
        
        print(f"\n✅ Done: {total_uploaded} uploaded, {failed} failed")
        return total_uploaded

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Streaming embedding pipeline")
    parser.add_argument("--limit", type=int, help="Process only first N images")
    parser.add_argument("--resume", action="store_true", help="Skip already processed images")
    args = parser.parse_args()
    
    skip = set()
    if args.resume:
        from vector_db.supabase_client import get_all_embeddings
        print("📂 Fetching existing embeddings...")
        existing = get_all_embeddings()
        skip = {r["content_hash"] for r in existing}
        print(f"   Skipping {len(skip)} already processed")
    
    pipeline = EmbeddingPipeline()
    asyncio.run(pipeline.run(limit=args.limit, skip_existing=skip if skip else None))

if __name__ == "__main__":
    main()



