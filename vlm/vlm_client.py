import json, time, sys # Qwen3-VL client for Stanford endpoint
from pathlib import Path
from openai import OpenAI
sys.path.insert(0, str(Path(__file__).parent.parent))
from vlm.config_vlm import STANFORD_ENDPOINT, STANFORD_API_KEY, STANFORD_MODEL, VLM_MAX_TOKENS, VLM_TEMPERATURE

_client = None

def get_client() -> OpenAI: # Lazy singleton client
    global _client
    if _client is None: _client = OpenAI(api_key=STANFORD_API_KEY, base_url=STANFORD_ENDPOINT)
    return _client

def call_vlm(image_url: str, prompt: str, max_retries: int = 3) -> dict | None:
    """Call Qwen3-VL with image and prompt, return parsed JSON"""
    client = get_client()
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=STANFORD_MODEL,
                messages=[{"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_url}}, {"type": "text", "text": prompt}]}],
                max_tokens=VLM_MAX_TOKENS, temperature=VLM_TEMPERATURE
            )
            raw = response.choices[0].message.content
            return parse_json_response(raw)
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"   ⚠️ Retry {attempt + 1}/{max_retries} after {wait}s: {e}")
                time.sleep(wait)
            else:
                print(f"   ❌ Failed after {max_retries} attempts: {e}")
                return None
    return None

def parse_json_response(raw: str) -> dict | None:
    """Parse JSON from VLM response, handling markdown code blocks"""
    try:
        text = raw.strip()
        if "```" in text: # Remove markdown code blocks
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"): part = part[4:].strip()
                if part.startswith("{"):
                    text = part
                    break
        if text.startswith("{") and text.endswith("}"): return json.loads(text)
        start, end = text.find("{"), text.rfind("}") # Try to find JSON object
        if start != -1 and end != -1: return json.loads(text[start:end + 1])
    except json.JSONDecodeError as e:
        print(f"   ⚠️ JSON parse error: {e}")
    return None

def test_connection() -> bool:
    """Test if Stanford endpoint is available"""
    try:
        client = get_client()
        models = client.models.list()
        print(f"✅ Connected to Stanford endpoint, model: {models.data[0].id}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def call_vlm_batch(images: list[dict], prompt: str, desc: str = "Processing") -> list[dict]:
    """Process multiple images with VLM"""
    from tqdm import tqdm
    results = []
    for img in tqdm(images, desc=desc):
        result = call_vlm(img["image_url"], prompt)
        results.append({"content_hash": img["content_hash"], "image_url": img["image_url"], "vlm_output": result, "status": "success" if result else "failed"})
    return results

if __name__ == "__main__":
    print("🔍 Testing Stanford VLM endpoint...")
    if test_connection():
        test_url = "https://i.pinimg.com/originals/b8/23/c3/b823c39c1471ddac40893452cb004e03.jpg"
        result = call_vlm(test_url, "Describe this image in one sentence.")
        print(f"Test result: {result}")



