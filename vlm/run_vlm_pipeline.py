import json, sys # Main VLM pipeline: run Qwen3-VL on filtered high-quality images
from pathlib import Path
from tqdm import tqdm
sys.path.insert(0, str(Path(__file__).parent.parent))
from vlm.config_vlm import STYLE_PROMPT, SCORING_PROMPT, VLM_RESULTS_JSON, OUTPUT_DIR
from vlm.vlm_client import call_vlm, test_connection
from vlm.filter_high_quality import filter_and_select_top_k

def load_filtered_clusters() -> list[dict]: # Load filtered clusters
    path = OUTPUT_DIR / "filtered_clusters.json"
    if not path.exists(): raise FileNotFoundError(f"Run filter_high_quality.py first: {path}")
    with open(path) as f: return json.load(f)

def run_vlm_on_clusters(resume: bool = True) -> list[dict]:
    """Run VLM on all filtered cluster representatives"""
    if not test_connection():
        print("❌ Stanford endpoint not available. Please check connection.")
        return []
    clusters = load_filtered_clusters()
    print(f"📊 Processing {len(clusters)} clusters with high-quality images")
    results_cache = {}
    if resume and VLM_RESULTS_JSON.exists(): # Load existing results
        with open(VLM_RESULTS_JSON) as f: 
            for r in json.load(f): results_cache[r["content_hash"]] = r
        print(f"   Resuming: {len(results_cache)} images already processed")
    all_results = []
    for cluster in tqdm(clusters, desc="Clusters"):
        cluster_id = cluster["cluster_id"]
        reps = cluster["high_quality_reps"]
        cluster_results = {"cluster_id": cluster_id, "size": cluster["size"], "image_results": []}
        for rep in reps:
            hash_ = rep["content_hash"]
            if hash_ in results_cache: # Use cached result
                cluster_results["image_results"].append(results_cache[hash_])
                continue
            url = rep["image_url"]
            print(f"\n   🖼️ Cluster {cluster_id}: {url[:60]}...")
            style_result = call_vlm(url, STYLE_PROMPT) # Call VLM for style
            score_result = call_vlm(url, SCORING_PROMPT) # Call VLM for scoring
            img_result = {"content_hash": hash_, "image_url": url, "qalign_aesthetic": rep.get("qalign_aesthetic"), "qalign_quality": rep.get("qalign_quality"), "style": style_result, "scores": score_result, "status": "success" if style_result and score_result else "partial"}
            cluster_results["image_results"].append(img_result)
            results_cache[hash_] = img_result
            if len(results_cache) % 5 == 0: # Checkpoint every 5 images
                _save_results(list(results_cache.values()))
        all_results.append(cluster_results)
    _save_results(list(results_cache.values()))
    output_path = OUTPUT_DIR / "cluster_vlm_results.json"
    with open(output_path, "w") as f: json.dump(all_results, f, indent=2)
    print(f"\n✅ Saved cluster results to {output_path}")
    return all_results

def _save_results(results: list[dict]):
    VLM_RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(VLM_RESULTS_JSON, "w") as f: json.dump(results, f, indent=2)

def run_vlm_single_cluster(cluster_id: int) -> dict | None:
    """Run VLM on a single cluster (for testing)"""
    if not test_connection(): return None
    clusters = load_filtered_clusters()
    cluster = next((c for c in clusters if c["cluster_id"] == cluster_id), None)
    if not cluster:
        print(f"❌ Cluster {cluster_id} not found")
        return None
    print(f"📊 Processing cluster {cluster_id} with {len(cluster['high_quality_reps'])} images")
    results = []
    for rep in cluster["high_quality_reps"]:
        url = rep["image_url"]
        print(f"   🖼️ {url[:60]}...")
        style = call_vlm(url, STYLE_PROMPT)
        scores = call_vlm(url, SCORING_PROMPT)
        results.append({"content_hash": rep["content_hash"], "image_url": url, "qalign_aesthetic": rep.get("qalign_aesthetic"), "style": style, "scores": scores})
    return {"cluster_id": cluster_id, "results": results}

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run VLM pipeline on filtered images")
    parser.add_argument("--cluster", type=int, default=None, help="Process single cluster (for testing)")
    parser.add_argument("--no-resume", action="store_true", help="Start fresh")
    args = parser.parse_args()
    if args.cluster is not None:
        result = run_vlm_single_cluster(args.cluster)
        if result: print(json.dumps(result, indent=2))
    else:
        run_vlm_on_clusters(resume=not args.no_resume)

if __name__ == "__main__": main()



