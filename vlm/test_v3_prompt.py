#!/usr/bin/env python3
"""Test V3 Image-to-Prompt on all sample images"""
import sys, json, base64, httpx, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from settings import STANFORD_ENDPOINT, STANFORD_API_KEY, STANFORD_MODEL, VLM_MAX_TOKENS, VLM_TEMPERATURE, IMAGE_TO_PROMPT

SAMPLE_DIR = Path(__file__).parent.parent / "output" / "sample_images"
OUTPUT_FILE = SAMPLE_DIR / "v3_prompts.json"

async def analyze_image(client: httpx.AsyncClient, image_path: Path) -> dict:
    """Send image to VLM and get JSON prompt"""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = image_path.suffix.lower().replace(".", "")
    mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
    
    payload = {
        "model": STANFORD_MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            {"type": "text", "text": IMAGE_TO_PROMPT}
        ]}],
        "max_tokens": VLM_MAX_TOKENS,
        "temperature": VLM_TEMPERATURE
    }
    
    try:
        resp = await client.post(f"{STANFORD_ENDPOINT}/chat/completions", json=payload, headers={"Authorization": f"Bearer {STANFORD_API_KEY}"}, timeout=120)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        content = content.strip()
        if content.startswith("```"): content = content.split("```")[1].lstrip("json\n") # Strip markdown
        return {"status": "success", "result": json.loads(content)}
    except json.JSONDecodeError as e:
        return {"status": "json_error", "error": str(e), "raw": content[:500]}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def main():
    images = sorted(SAMPLE_DIR.glob("*.jpg"))
    print(f"Found {len(images)} images to process\n")
    
    results = {}
    async with httpx.AsyncClient() as client:
        for img in images:
            print(f"Processing: {img.name}...", end=" ", flush=True)
            result = await analyze_image(client, img)
            results[img.name] = result
            status = "✅" if result["status"] == "success" else "❌"
            print(status)
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    success = sum(1 for r in results.values() if r["status"] == "success")
    print(f"\n{'='*50}")
    print(f"Results: {success}/{len(images)} successful")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
