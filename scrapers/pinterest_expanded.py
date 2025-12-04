#!/usr/bin/env python3
"""Pinterest Expanded Scraper - Uses Visual Techniques Taxonomy keywords
Builds on existing master_scraper.py but with new art/technique keywords
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.expanded_keywords import get_all_pinterest_keywords, ART_MOVEMENTS, VISUAL_TECHNIQUES, AD_TYPES, BRAND_AESTHETICS, INDUSTRY_VISUALS

def generate_expanded_config():
    """Generate expanded CATEGORIES dict for config.py format"""
    categories = {}
    
    # Art Movements
    for name, data in ART_MOVEMENTS.items():
        for i, term in enumerate(data["search_terms"][:3]):  # Top 3 per movement
            key = f"art_{name}_{i+1}"
            categories[key] = {"search": term, "type": "art_movement"}
    
    # Visual Techniques  
    for name, data in VISUAL_TECHNIQUES.items():
        for i, term in enumerate(data["search_terms"][:2]):  # Top 2 per technique
            key = f"tech_{name}_{i+1}"
            categories[key] = {"search": term, "type": "technique"}
    
    # Ad Types
    for name, data in AD_TYPES.items():
        for i, term in enumerate(data["search_terms"][:2]):
            key = f"ad_{name}_{i+1}"
            categories[key] = {"search": term, "type": "ad_format"}
    
    # Brand Aesthetics
    for name, data in BRAND_AESTHETICS.items():
        for i, term in enumerate(data["search_terms"][:2]):
            key = f"brand_{name}_{i+1}"
            categories[key] = {"search": term, "type": "brand_aesthetic"}
    
    # Industry
    for name, data in INDUSTRY_VISUALS.items():
        for i, term in enumerate(data["search_terms"][:2]):
            key = f"ind_{name}_{i+1}"
            categories[key] = {"search": term, "type": "industry"}
    
    return categories

def print_expanded_config():
    """Print the expanded config for copy-paste into config.py"""
    categories = generate_expanded_config()
    
    print(f"# === EXPANDED CATEGORIES ({len(categories)} total) ===")
    print("EXPANDED_CATEGORIES = {")
    
    current_type = None
    for key, val in categories.items():
        if val["type"] != current_type:
            current_type = val["type"]
            print(f"\n    # === {current_type.upper()} ===")
        print(f'    "{key}": {{"search": "{val["search"]}", "type": "{val["type"]}"}},')
    
    print("}")
    print(f"\n# Total: {len(categories)} new categories")

def get_expanded_category_order():
    """Get ordered list of expanded category keys"""
    categories = generate_expanded_config()
    return list(categories.keys())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Pinterest expanded keywords")
    parser.add_argument("--print-config", action="store_true", help="Print config for config.py")
    parser.add_argument("--count", action="store_true", help="Just show count")
    args = parser.parse_args()
    
    if args.print_config:
        print_expanded_config()
    elif args.count:
        categories = generate_expanded_config()
        print(f"📊 Expanded categories: {len(categories)}")
        from collections import Counter
        types = Counter(v["type"] for v in categories.values())
        for t, c in types.items():
            print(f"   - {t}: {c}")
    else:
        # Default: show summary
        keywords = get_all_pinterest_keywords()
        print(f"📊 Total Pinterest search terms: {len(keywords)}")
        print("\nRun with --print-config to get config.py format")



