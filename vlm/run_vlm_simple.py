#!/usr/bin/env python3
"""Simple reliable VLM batch processing - one at a time with progress"""
import json, base64, httpx, sys, time
from pathlib import Path
from tqdm import tqdm
from PIL import Image
from io import BytesIO
sys.path.insert(0, str(Path(__file__).parent.parent))
from settings import IMAGE_TO_PROMPT, CLUSTERS_JSON, OUTPUT_DIR

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3-vl:8b"
OUTPUT_FILE = OUTPUT_DIR / "vlm_results_v3.json"
TIMEOUT = 180  # 3 minutes per image
MAX_RETRIES = 2

def load_images():
    with open(CLUSTERS_JSON) as f:
        clusters = json.load(f)
    images = []
    for c in clusters:
        for rep in c.get("representatives", [])[:5]:
            images.append({"content_hash": rep["content_hash"], "image_url": rep["image_url"], "cluster_id": c["cluster_id"]})
    return images

def download_image(url: str) -> bytes | None:
    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            data = resp.content
            if len(data) > 5 * 1024 * 1024:  # >5MB, resize
                img = Image.open(BytesIO(data))
                img.thumbnail((1024, 1024))
                buf = BytesIO()
                img.save(buf, format="JPEG", quality=85)
                return buf.getvalue()
            return data
    except: pass
    return None

def analyze(img_data: bytes) -> dict | None:
    b64 = base64.b64encode(img_data).decode()
    payload = {"model": MODEL, "messages": [{"role": "user", "content": IMAGE_TO_PROMPT, "images": [b64]}], "stream": False, "options": {"temperature": 0.3}}
    try:
        resp = httpx.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        content = resp.json()["message"]["content"].strip()
        if content.startswith("```"): content = content.split("```")[1].lstrip("json\n")
        if content.endswith("```"): content = content.rsplit("```", 1)[0]
        return json.loads(content)
    except: pass
    return None

def main():
    images = load_images()
    print(f"📊 Total: {len(images)} images")
    
    results = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            results = {r["content_hash"]: r for r in json.load(f) if r.get("status") == "success"}
        print(f"   Resume: {len(results)} done")
    
    to_do = [img for img in images if img["content_hash"] not in results]
    print(f"   Remaining: {len(to_do)}\n")
    
    for img in tqdm(to_do, desc="Processing"):
        for attempt in range(MAX_RETRIES):
            img_data = download_image(img["image_url"])
            if not img_data:
                results[img["content_hash"]] = {"content_hash": img["content_hash"], "status": "download_failed"}
                break
            
            result = analyze(img_data)
            if result:
                results[img["content_hash"]] = {"content_hash": img["content_hash"], "image_url": img["image_url"], "cluster_id": img["cluster_id"], "status": "success", "result": result}
                break
            time.sleep(1)
        else:
            results[img["content_hash"]] = {"content_hash": img["content_hash"], "status": "error"}
        
        if len(results) % 10 == 0:  # Save every 10
            with open(OUTPUT_FILE, "w") as f:
                json.dump(list(results.values()), f, ensure_ascii=False)
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(list(results.values()), f, indent=2, ensure_ascii=False)
    
    success = sum(1 for r in results.values() if r.get("status") == "success")
    print(f"\n✅ Done: {success}/{len(images)} success")

if __name__ == "__main__":
    main()
