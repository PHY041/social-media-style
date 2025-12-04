import json # Cluster data service
from pathlib import Path
from functools import lru_cache
from collections import Counter

CLUSTERS_PATH = Path(__file__).parent.parent / "output" / "clusters.json"
_clusters_cache = None

def _load_clusters() -> list[dict]: # Load clusters from JSON (cached)
    global _clusters_cache
    if _clusters_cache is None:
        if not CLUSTERS_PATH.exists(): raise FileNotFoundError(f"clusters.json not found at {CLUSTERS_PATH}")
        with open(CLUSTERS_PATH) as f: _clusters_cache = json.load(f)
    return _clusters_cache

def get_all_clusters() -> list[dict]: # Get summary of all clusters
    clusters = _load_clusters()
    summaries = []
    for c in clusters:
        reps = c.get("representatives", [])
        cats = [r.get("category", "unknown") for r in reps]
        top_cats = [cat for cat, _ in Counter(cats).most_common(3)]
        previews = [r.get("image_url") for r in reps[:3] if r.get("image_url")]
        summaries.append({"cluster_id": c["cluster_id"], "size": c["size"], "top_categories": top_cats, "preview_images": previews})
    return sorted(summaries, key=lambda x: x["size"], reverse=True)

def get_cluster_by_id(cluster_id: int) -> dict | None: # Get single cluster detail
    clusters = _load_clusters()
    for c in clusters:
        if c["cluster_id"] == cluster_id:
            return {"cluster_id": c["cluster_id"], "size": c["size"], "representatives": c.get("representatives", []), "center_embedding": c.get("center_embedding")}
    return None

def get_stats() -> dict: # Get system stats
    clusters = _load_clusters()
    total_images = sum(c["size"] for c in clusters)
    cat_dist = Counter()
    for c in clusters:
        for r in c.get("representatives", []): cat_dist[r.get("category", "unknown")] += 1
    return {"total_images": total_images, "total_clusters": len(clusters), "category_distribution": dict(cat_dist.most_common())}

def reload_clusters(): # Force reload clusters (if updated)
    global _clusters_cache
    _clusters_cache = None
    return _load_clusters()

