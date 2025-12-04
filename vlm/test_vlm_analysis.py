#!/usr/bin/env python3
"""Test VLM style analysis on sample images"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vlm.vlm_client import call_vlm, test_connection
from vlm.vlm_prompt import STYLE_ANALYSIS_PROMPT, STYLE_ANALYSIS_PROMPT_COMPACT

# Sample images for testing (high-quality Pinterest images)
TEST_IMAGES = [
    {
        "name": "Luxury Bag",
        "url": "https://i.pinimg.com/originals/4e/9e/94/4e9e944d52c7e8d86b32b5d9a2a94ff3.jpg"
    },
    {
        "name": "Skincare Flat Lay",
        "url": "https://i.pinimg.com/originals/e7/8d/d3/e78dd3a5f3c25f6a7e0a09b5d2c91cbb.jpg"
    },
    {
        "name": "Food Photography",
        "url": "https://i.pinimg.com/originals/b8/23/c3/b823c39c1471ddac40893452cb004e03.jpg"
    }
]


def test_single_image(image_url: str, image_name: str, use_compact: bool = False):
    """Test VLM on a single image"""
    prompt = STYLE_ANALYSIS_PROMPT_COMPACT if use_compact else STYLE_ANALYSIS_PROMPT
    
    print(f"\n{'='*60}")
    print(f"📸 Testing: {image_name}")
    print(f"🔗 URL: {image_url[:80]}...")
    print(f"📝 Using: {'Compact' if use_compact else 'Full'} prompt")
    print("="*60)
    
    result = call_vlm(image_url, prompt)
    
    if result:
        print("\n✅ Success! Output:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    else:
        print("\n❌ Failed to get valid JSON response")
        return None


def main():
    print("🚀 VLM Style Analysis Test")
    print("="*60)
    
    # Test connection first
    if not test_connection():
        print("❌ Cannot connect to Stanford endpoint. Exiting.")
        return
    
    print("\n" + "="*60)
    print("Choose test mode:")
    print("1. Test single image (full prompt)")
    print("2. Test single image (compact prompt)")
    print("3. Test all sample images (compact)")
    print("="*60)
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        test_single_image(TEST_IMAGES[0]["url"], TEST_IMAGES[0]["name"], use_compact=False)
    elif choice == "2":
        test_single_image(TEST_IMAGES[0]["url"], TEST_IMAGES[0]["name"], use_compact=True)
    elif choice == "3":
        results = []
        for img in TEST_IMAGES:
            result = test_single_image(img["url"], img["name"], use_compact=True)
            results.append({"name": img["name"], "result": result})
        
        # Summary
        print("\n" + "="*60)
        print("📊 Summary")
        print("="*60)
        success = sum(1 for r in results if r["result"])
        print(f"Success: {success}/{len(results)}")
        
        # Save results
        output_file = Path(__file__).parent.parent / "output" / "vlm_test_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Results saved to: {output_file}")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()

