import json, sys # UMAP visualization of embeddings
import numpy as np
import umap
import matplotlib.pyplot as plt
from pathlib import Path
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from embedding.config_embed import UMAP_OUTPUT_DIR, CLUSTERS_JSON
from clustering.kmeans_cluster import load_embeddings

def run_umap(embeddings: np.ndarray, n_components: int = 2, n_neighbors: int = 15, min_dist: float = 0.1) -> np.ndarray:  # Reduce embeddings to 2D/3D
    print(f"🗺️ Running UMAP (n_components={n_components})...")
    reducer = umap.UMAP(n_components=n_components, n_neighbors=n_neighbors, min_dist=min_dist, random_state=42, metric="cosine")
    return reducer.fit_transform(embeddings)

def plot_by_category_type(coords: np.ndarray, data: list[dict], output_path: Path):  # Color by category_type
    plt.figure(figsize=(14, 10))
    types = list(set(d["category_type"] for d in data))
    colors = plt.cm.Set2(np.linspace(0, 1, len(types)))
    type_to_color = dict(zip(types, colors))
    
    for t in types:
        mask = [d["category_type"] == t for d in data]
        pts = coords[mask]
        plt.scatter(pts[:, 0], pts[:, 1], c=[type_to_color[t]], label=t, alpha=0.5, s=5)
    
    plt.legend(markerscale=3)
    plt.title("Pinterest Embeddings by Category Type")
    plt.xlabel("UMAP 1")
    plt.ylabel("UMAP 2")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"   💾 Saved: {output_path}")

def plot_by_category(coords: np.ndarray, data: list[dict], output_path: Path, top_n: int = 15):  # Color by top N categories
    plt.figure(figsize=(14, 10))
    from collections import Counter
    cat_counts = Counter(d["category"] for d in data)
    top_cats = [c for c, _ in cat_counts.most_common(top_n)]
    colors = plt.cm.tab20(np.linspace(0, 1, len(top_cats)))
    cat_to_color = dict(zip(top_cats, colors))
    
    other_mask = [d["category"] not in top_cats for d in data]  # Plot "other" first
    if any(other_mask): plt.scatter(coords[other_mask, 0], coords[other_mask, 1], c="lightgray", alpha=0.3, s=3, label="other")
    
    for cat in top_cats:
        mask = [d["category"] == cat for d in data]
        pts = coords[mask]
        plt.scatter(pts[:, 0], pts[:, 1], c=[cat_to_color[cat]], label=cat, alpha=0.6, s=5)
    
    plt.legend(markerscale=3, loc="upper right", fontsize=8)
    plt.title(f"Pinterest Embeddings by Category (Top {top_n})")
    plt.xlabel("UMAP 1")
    plt.ylabel("UMAP 2")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"   💾 Saved: {output_path}")

def plot_by_cluster(coords: np.ndarray, data: list[dict], output_path: Path):  # Color by cluster_id (requires clusters.json)
    if not CLUSTERS_JSON.exists():
        print("   ⚠️ clusters.json not found, skipping cluster plot")
        return
    
    with open(CLUSTERS_JSON) as f: clusters = json.load(f)
    hash_to_cluster = {}
    for c in clusters:
        for rep in c.get("representatives", []):
            hash_to_cluster[rep["content_hash"]] = c["cluster_id"]
    
    cluster_ids = [hash_to_cluster.get(d["content_hash"], -1) for d in data]
    n_clusters = max(cluster_ids) + 1
    
    plt.figure(figsize=(14, 10))
    colors = plt.cm.nipy_spectral(np.linspace(0, 1, n_clusters))
    
    for cid in range(n_clusters):
        mask = [c == cid for c in cluster_ids]
        if not any(mask): continue
        pts = coords[mask]
        plt.scatter(pts[:, 0], pts[:, 1], c=[colors[cid]], alpha=0.5, s=5)
    
    plt.title(f"Pinterest Embeddings by Cluster (K={n_clusters})")
    plt.xlabel("UMAP 1")
    plt.ylabel("UMAP 2")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"   💾 Saved: {output_path}")

def create_interactive_html(coords: np.ndarray, data: list[dict], output_path: Path):  # Create interactive Plotly HTML
    try:
        import plotly.express as px
        import pandas as pd
    except ImportError:
        print("   ⚠️ plotly not installed, skipping interactive HTML")
        return
    
    df = pd.DataFrame({"x": coords[:, 0], "y": coords[:, 1], "category": [d["category"] for d in data], "category_type": [d["category_type"] for d in data], "url": [d["image_url"] for d in data]})
    fig = px.scatter(df, x="x", y="y", color="category_type", hover_data=["category", "url"], title="Pinterest Style Universe", opacity=0.6)
    fig.update_traces(marker=dict(size=4))
    fig.write_html(output_path)
    print(f"   💾 Saved: {output_path}")

def run_visualization():  # Main visualization pipeline
    UMAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    hashes, embeddings, data = load_embeddings()
    coords = run_umap(embeddings, n_components=2)
    
    print("🎨 Generating plots...")
    plot_by_category_type(coords, data, UMAP_OUTPUT_DIR / "umap_by_type.png")
    plot_by_category(coords, data, UMAP_OUTPUT_DIR / "umap_by_category.png")
    plot_by_cluster(coords, data, UMAP_OUTPUT_DIR / "umap_by_cluster.png")
    create_interactive_html(coords, data, UMAP_OUTPUT_DIR / "umap_interactive.html")
    
    np.save(UMAP_OUTPUT_DIR / "umap_coords.npy", coords)  # Save coordinates for reuse
    print(f"\n✅ Visualization complete. Files in: {UMAP_OUTPUT_DIR}")

if __name__ == "__main__":
    run_visualization()



