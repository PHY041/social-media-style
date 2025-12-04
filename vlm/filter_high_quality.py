import json, sys # Filter high-quality images and select top-K per cluster
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent.parent))
from vlm.config_vlm import QALIGN_SCORES_JSON, CLUSTERS_JSON, TOP_K_PER_CLUSTER, QALIGN_MIN_SCORE, OUTPUT_DIR

def load_qalign_scores() -> dict[str, dict]: # Load Q-Align scores as hash -> score dict
    if not QALIGN_SCORES_JSON.exists(): raise FileNotFoundError(f"Run qalign_scorer.py first: {QALIGN_SCORES_JSON}")
    with open(QALIGN_SCORES_JSON) as f: data = json.load(f)
    return {r["content_hash"]: r for r in data if r.get("qalign_aesthetic") is not None}

def load_clusters() -> list[dict]: # Load clusters.json
    if not CLUSTERS_JSON.exists(): raise FileNotFoundError(f"clusters.json not found: {CLUSTERS_JSON}")
    with open(CLUSTERS_JSON) as f: return json.load(f)

def filter_and_select_top_k(top_k: int = TOP_K_PER_CLUSTER, min_score: float = QALIGN_MIN_SCORE) -> dict:
    """Filter clusters to only include high-quality images, select top-K per cluster"""
    scores = load_qalign_scores()
    clusters = load_clusters()
    print(f"📊 Loaded {len(scores)} Q-Align scores, {len(clusters)} clusters")
    print(f"   Filter threshold: >= {min_score}, Top-K: {top_k}")
    filtered_clusters = []
    total_passed, total_selected = 0, 0
    for cluster in clusters:
        cluster_id = cluster["cluster_id"]
        reps = cluster.get("representatives", [])
        scored_reps = [] # Score each representative
        for rep in reps:
            hash_ = rep["content_hash"]
            if hash_ in scores and scores[hash_]["qalign_aesthetic"] >= min_score:
                scored_reps.append({**rep, "qalign_aesthetic": scores[hash_]["qalign_aesthetic"], "qalign_quality": scores[hash_].get("qalign_quality")})
        total_passed += len(scored_reps)
        scored_reps.sort(key=lambda x: x["qalign_aesthetic"], reverse=True) # Sort by aesthetic score
        top_reps = scored_reps[:top_k]
        total_selected += len(top_reps)
        if top_reps:
            filtered_clusters.append({"cluster_id": cluster_id, "size": cluster["size"], "high_quality_reps": top_reps, "passed_filter": len(scored_reps), "original_reps": len(reps)})
    print(f"\n✅ Results:")
    print(f"   Clusters with high-quality images: {len(filtered_clusters)}/{len(clusters)}")
    print(f"   Total images passed filter: {total_passed}")
    print(f"   Total images selected (top-{top_k}): {total_selected}")
    output_path = OUTPUT_DIR / "filtered_clusters.json"
    with open(output_path, "w") as f: json.dump(filtered_clusters, f, indent=2)
    print(f"   💾 Saved to {output_path}")
    return {"filtered_clusters": filtered_clusters, "stats": {"clusters_with_hq": len(filtered_clusters), "total_passed": total_passed, "total_selected": total_selected}}

def get_all_high_quality_images(min_score: float = QALIGN_MIN_SCORE) -> list[dict]:
    """Get all images that passed the quality filter"""
    scores = load_qalign_scores()
    return [r for r in scores.values() if r["qalign_aesthetic"] >= min_score]

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Filter high-quality images")
    parser.add_argument("--top-k", type=int, default=TOP_K_PER_CLUSTER, help=f"Top K per cluster (default: {TOP_K_PER_CLUSTER})")
    parser.add_argument("--min-score", type=float, default=QALIGN_MIN_SCORE, help=f"Min Q-Align score (default: {QALIGN_MIN_SCORE})")
    args = parser.parse_args()
    filter_and_select_top_k(top_k=args.top_k, min_score=args.min_score)

if __name__ == "__main__": main()



