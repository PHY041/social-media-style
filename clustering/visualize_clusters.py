import json, sys # Quick visualization using cluster data (no Supabase fetch needed)
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from embedding.config_embed import CLUSTERS_JSON, UMAP_OUTPUT_DIR

def load_cluster_data():  # Load clusters.json
    with open(CLUSTERS_JSON) as f: return json.load(f)

def plot_cluster_summary(clusters: list[dict], output_dir: Path):  # Bar chart of cluster sizes
    output_dir.mkdir(parents=True, exist_ok=True)
    sizes = [c["size"] for c in sorted(clusters, key=lambda x: x["cluster_id"])]
    
    plt.figure(figsize=(16, 6))
    plt.bar(range(len(sizes)), sizes, color=plt.cm.viridis(np.linspace(0, 1, len(sizes))))
    plt.xlabel("Cluster ID")
    plt.ylabel("Number of Images")
    plt.title(f"Cluster Size Distribution (K={len(clusters)}, Total={sum(sizes):,})")
    plt.tight_layout()
    plt.savefig(output_dir / "cluster_sizes.png", dpi=150)
    plt.close()
    print(f"💾 Saved: {output_dir / 'cluster_sizes.png'}")

def plot_category_distribution(clusters: list[dict], output_dir: Path):  # Category breakdown
    from collections import Counter
    cats = Counter()
    for c in clusters:
        for rep in c.get("representatives", []):
            cats[rep["category"]] += 1
    
    top_cats = cats.most_common(20)
    labels, values = zip(*top_cats)
    
    plt.figure(figsize=(12, 8))
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    plt.barh(labels, values, color=colors)
    plt.xlabel("Count (in cluster representatives)")
    plt.title("Top 20 Categories in Cluster Representatives")
    plt.tight_layout()
    plt.savefig(output_dir / "category_distribution.png", dpi=150)
    plt.close()
    print(f"💾 Saved: {output_dir / 'category_distribution.png'}")

def plot_cluster_centers_umap(clusters: list[dict], output_dir: Path):  # UMAP on cluster centers only (120 points = fast)
    import umap
    centers = np.array([c["center_embedding"] for c in clusters])
    print(f"🗺️ Running UMAP on {len(centers)} cluster centers...")
    
    reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.3, random_state=42, metric="cosine")
    coords = reducer.fit_transform(centers)
    
    sizes = np.array([c["size"] for c in clusters])
    sizes_normalized = 50 + (sizes - sizes.min()) / (sizes.max() - sizes.min()) * 300  # Scale for visibility
    
    plt.figure(figsize=(14, 10))
    scatter = plt.scatter(coords[:, 0], coords[:, 1], c=range(len(clusters)), cmap="nipy_spectral", s=sizes_normalized, alpha=0.7)
    
    for i, c in enumerate(clusters):  # Label top clusters
        if c["size"] > 800:
            reps = c.get("representatives", [{}])
            label = reps[0].get("category", f"c{i}") if reps else f"c{i}"
            plt.annotate(label, (coords[i, 0], coords[i, 1]), fontsize=8, alpha=0.8)
    
    plt.colorbar(scatter, label="Cluster ID")
    plt.title(f"UMAP of Cluster Centers (K={len(clusters)}, bubble size = cluster size)")
    plt.xlabel("UMAP 1")
    plt.ylabel("UMAP 2")
    plt.tight_layout()
    plt.savefig(output_dir / "cluster_centers_umap.png", dpi=150)
    plt.close()
    print(f"💾 Saved: {output_dir / 'cluster_centers_umap.png'}")
    
    return coords

def generate_cluster_report(clusters: list[dict], output_dir: Path):  # Markdown report
    report = ["# Cluster Analysis Report\n"]
    report.append(f"**Total Clusters:** {len(clusters)}\n")
    report.append(f"**Total Images:** {sum(c['size'] for c in clusters):,}\n\n")
    report.append("## Top 20 Clusters by Size\n\n")
    report.append("| Cluster | Size | Top Categories |\n")
    report.append("|---------|------|----------------|\n")
    
    for c in sorted(clusters, key=lambda x: x["size"], reverse=True)[:20]:
        reps = c.get("representatives", [])
        cats = ", ".join(set(r["category"] for r in reps[:5]))
        report.append(f"| {c['cluster_id']} | {c['size']} | {cats} |\n")
    
    report.append("\n## Cluster Representatives\n\n")
    for c in sorted(clusters, key=lambda x: x["size"], reverse=True)[:10]:
        report.append(f"### Cluster {c['cluster_id']} ({c['size']} images)\n\n")
        for rep in c.get("representatives", [])[:3]:
            report.append(f"- [{rep['category']}]({rep['image_url']})\n")
        report.append("\n")
    
    with open(output_dir / "cluster_report.md", "w") as f: f.write("".join(report))
    print(f"💾 Saved: {output_dir / 'cluster_report.md'}")

def run_visualization():
    UMAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clusters = load_cluster_data()
    print(f"📊 Loaded {len(clusters)} clusters")
    
    plot_cluster_summary(clusters, UMAP_OUTPUT_DIR)
    plot_category_distribution(clusters, UMAP_OUTPUT_DIR)
    plot_cluster_centers_umap(clusters, UMAP_OUTPUT_DIR)
    generate_cluster_report(clusters, UMAP_OUTPUT_DIR)
    
    print(f"\n✅ Visualization complete! Files in: {UMAP_OUTPUT_DIR}")

if __name__ == "__main__":
    run_visualization()



