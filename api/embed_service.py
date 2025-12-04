import torch # Embedding service for API (lazy-loaded singleton)
import open_clip
from functools import lru_cache

_model, _preprocess, _tokenizer = None, None, None

def _load_model(): # Lazy load model on first use
    global _model, _preprocess, _tokenizer
    if _model is None:
        device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
        _model, _, _preprocess = open_clip.create_model_and_transforms("ViT-L-14", pretrained="laion2b_s32b_b82k", device=device)
        _tokenizer = open_clip.get_tokenizer("ViT-L-14")
        _model.eval()
    return _model, _preprocess, _tokenizer

def get_text_embedding(query: str) -> list[float]: # Encode text query to 768-dim vector
    model, _, tokenizer = _load_model()
    device = next(model.parameters()).device
    with torch.no_grad():
        tokens = tokenizer([query]).to(device)
        emb = model.encode_text(tokens)
        emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb[0].cpu().tolist()

async def get_image_embedding(image_url: str) -> list[float]: # Encode image URL to 768-dim vector
    import aiohttp
    from PIL import Image
    from io import BytesIO
    model, preprocess, _ = _load_model()
    device = next(model.parameters()).device
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200: raise ValueError(f"Failed to fetch image: {resp.status}")
            data = await resp.read()
    img = Image.open(BytesIO(data)).convert("RGB")
    with torch.no_grad():
        img_tensor = preprocess(img).unsqueeze(0).to(device)
        emb = model.encode_image(img_tensor)
        emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb[0].cpu().tolist()

def warmup_model(): # Pre-load model on startup
    _load_model()
    return True

