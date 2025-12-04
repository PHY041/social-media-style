import json, sys # Generate Prompt DNA from VLM results
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).parent.parent))
from vlm.config_vlm import OUTPUT_DIR, PROMPT_DNA_JSON, CLUSTER_META_JSON

def load_vlm_results() -> list[dict]:
    path = OUTPUT_DIR / "cluster_vlm_results.json"
    if not path.exists(): raise FileNotFoundError(f"Run run_vlm_pipeline.py first: {path}")
    with open(path) as f: return json.load(f)

def aggregate_cluster_style(image_results: list[dict]) -> dict:
    """Aggregate multiple image VLM results into cluster-level style"""
    if not image_results: return {}
    keywords_all, colors_all, use_cases_all, prompts_all = [], [], [], []
    lightings, compositions, moods, categories = [], [], [], []
    scores = {"commercial": [], "brand_fit": [], "attention": [], "production": []}
    for img in image_results:
        style = img.get("style") or {}
        score = img.get("scores") or {}
        keywords_all.extend(style.get("keywords", []))
        colors_all.extend(style.get("color_palette", []))
        use_cases_all.extend(style.get("commercial_use", []))
        if style.get("generation_prompt"): prompts_all.append(style["generation_prompt"])
        if style.get("lighting"): lightings.append(style["lighting"])
        if style.get("composition"): compositions.append(style["composition"])
        if style.get("mood"): moods.append(style["mood"])
        if score.get("style_category"): categories.append(score["style_category"])
        if score.get("commercial_score"): scores["commercial"].append(score["commercial_score"])
        if score.get("brand_fit"): scores["brand_fit"].append(score["brand_fit"])
        if score.get("attention_grabbing"): scores["attention"].append(score["attention_grabbing"])
        if score.get("production_quality"): scores["production"].append(score["production_quality"])
    def top_n(items, n=10): return [item for item, _ in Counter(items).most_common(n)]
    def most_common(items): return Counter(items).most_common(1)[0][0] if items else None
    def avg(nums): return round(sum(nums) / len(nums), 2) if nums else None
    return {
        "keywords": top_n(keywords_all, 15), "color_palette": top_n(colors_all, 6), "commercial_use": top_n(use_cases_all, 5),
        "lighting": most_common(lightings), "composition": most_common(compositions), "mood": most_common(moods),
        "style_category": most_common(categories), "sample_prompts": prompts_all[:3],
        "avg_scores": {"commercial": avg(scores["commercial"]), "brand_fit": avg(scores["brand_fit"]), "attention": avg(scores["attention"]), "production": avg(scores["production"])}
    }

def generate_prompt_dna(cluster_style: dict, cluster_id: int) -> dict:
    """Generate Prompt DNA from aggregated cluster style"""
    keywords = cluster_style.get("keywords", [])
    colors = cluster_style.get("color_palette", [])
    lighting = cluster_style.get("lighting", "professional lighting")
    composition = cluster_style.get("composition", "well-composed")
    mood = cluster_style.get("mood", "professional")
    category = cluster_style.get("style_category", "commercial")
    base_elements = [mood, category, "commercial photography", lighting, composition]
    if colors: base_elements.append(f"color palette: {', '.join(colors[:3])}")
    base_prompt = ", ".join([e for e in base_elements if e])
    style_modifiers = keywords[:8] if keywords else []
    negative_modifiers = ["low quality", "blurry", "amateur", "poorly lit", "cluttered background", "overexposed", "underexposed"]
    return {"cluster_id": cluster_id, "base_prompt": base_prompt, "style_modifiers": style_modifiers, "negative_modifiers": negative_modifiers, "sample_prompts": cluster_style.get("sample_prompts", []), "metadata": {"style_category": category, "mood": mood, "avg_scores": cluster_style.get("avg_scores", {})}}

def generate_all_prompt_dna() -> list[dict]:
    """Generate Prompt DNA for all clusters"""
    vlm_results = load_vlm_results()
    print(f"📊 Generating Prompt DNA for {len(vlm_results)} clusters")
    all_dna, all_meta = [], []
    for cluster in vlm_results:
        cluster_id = cluster["cluster_id"]
        image_results = cluster.get("image_results", [])
        if not image_results: continue
        style = aggregate_cluster_style(image_results)
        dna = generate_prompt_dna(style, cluster_id)
        all_dna.append(dna)
        qalign_scores = [img.get("qalign_aesthetic") for img in image_results if img.get("qalign_aesthetic")]
        meta = {"cluster_id": cluster_id, "size": cluster.get("size", 0), "num_hq_images": len(image_results), "avg_qalign": round(sum(qalign_scores) / len(qalign_scores), 3) if qalign_scores else None, **style}
        all_meta.append(meta)
    with open(PROMPT_DNA_JSON, "w") as f: json.dump(all_dna, f, indent=2)
    print(f"✅ Saved Prompt DNA to {PROMPT_DNA_JSON}")
    with open(CLUSTER_META_JSON, "w") as f: json.dump(all_meta, f, indent=2)
    print(f"✅ Saved Cluster Meta to {CLUSTER_META_JSON}")
    return all_dna

def print_sample_dna(cluster_id: int = None):
    """Print sample Prompt DNA for inspection"""
    if not PROMPT_DNA_JSON.exists():
        print("❌ Run generate_all_prompt_dna() first")
        return
    with open(PROMPT_DNA_JSON) as f: all_dna = json.load(f)
    if cluster_id:
        dna = next((d for d in all_dna if d["cluster_id"] == cluster_id), None)
        if dna: print(json.dumps(dna, indent=2))
        else: print(f"Cluster {cluster_id} not found")
    else:
        print(f"Sample Prompt DNA (first 3 clusters):")
        for dna in all_dna[:3]: print(json.dumps(dna, indent=2)); print("-" * 50)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate Prompt DNA from VLM results")
    parser.add_argument("--show", type=int, default=None, help="Show DNA for specific cluster")
    args = parser.parse_args()
    if args.show: print_sample_dna(args.show)
    else: generate_all_prompt_dna()

if __name__ == "__main__": main()



