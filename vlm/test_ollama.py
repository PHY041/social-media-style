#!/usr/bin/env python3
"""Test V3 Image-to-Prompt using local Ollama Qwen3-VL"""
import json, base64, httpx, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from settings import IMAGE_TO_PROMPT

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3-vl:8b"  # 6.1GB, fast on M3 Max
SAMPLE_DIR = Path(__file__).parent.parent / "output" / "sample_images"
OUTPUT_FILE = SAMPLE_DIR / "v3_prompts_ollama.json"

def analyze_image(image_path: Path) -> dict:
    """Send image to Ollama and get JSON prompt"""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    
    payload = {"model": MODEL, "messages": [{"role": "user", "content": IMAGE_TO_PROMPT, "images": [b64]}], "stream": False, "options": {"temperature": 0.3}}
    
    try:
        resp = httpx.post(OLLAMA_URL, json=payload, timeout=300)
        resp.raise_for_status()
        content = resp.json()["message"]["content"]
        content = content.strip()
        if content.startswith("```"): content = content.split("```")[1].lstrip("json\n")  # Strip markdown
        if content.endswith("```"): content = content.rsplit("```", 1)[0]
        return {"status": "success", "result": json.loads(content)}
    except json.JSONDecodeError as e:
        return {"status": "json_error", "error": str(e), "raw": content[:1000] if 'content' in dir() else "no content"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    images = sorted(SAMPLE_DIR.glob("*.jpg"))
    print(f"🖼️  Found {len(images)} images")
    print(f"🤖 Using model: {MODEL}\n")
    
    results = {}
    for i, img in enumerate(images, 1):
        print(f"[{i}/{len(images)}] {img.name}...", end=" ", flush=True)
        result = analyze_image(img)
        results[img.name] = result
        print("✅" if result["status"] == "success" else f"❌ ({result.get('error', 'json_error')[:30]})")
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    success = sum(1 for r in results.values() if r["status"] == "success")
    print(f"\n{'='*50}")
    print(f"✅ Results: {success}/{len(images)} successful")
    print(f"📁 Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
