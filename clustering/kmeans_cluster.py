import json, sys # K-means clustering with representatives extraction
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from tqdm import tqdm
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from embedding.config_embed import DEFAULT_K, K_CANDIDATES, CLUSTER_REPRESENTATIVES, CLUSTERS_JSON
from vector_db.supabase_client import get_all_embeddings, batch_update_clusters

def load_embeddings() -> tuple[list[str], np.ndarray, list[dict]]:  # Fetch embeddings from Supabase
    import json
    print("📂 Loading embeddings from Supabase...")
    data = get_all_embeddings()
    if not data: raise ValueError("No embeddings found in database")
    hashes = [d["content_hash"] for d in data]
    emb_list = []
    for d in data:  # Handle string or list embeddings
        emb = d["embedding"]
        emb_list.append(json.loads(emb) if isinstance(emb, str) else emb)
    embeddings = np.array(emb_list, dtype=np.float32)
    print(f"   Loaded {len(hashes)} embeddings, dim={embeddings.shape[1]}")
    return hashes, embeddings, data

def run_kmeans(embeddings: np.ndarray, k: int = DEFAULT_K) -> tuple[np.ndarray, np.ndarray]:  # Run K-means clustering
    print(f"🔄 Running K-means with K={k}...")
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
    labels = kmeans.fit_predict(embeddings)
    centers = kmeans.cluster_centers_
    print(f"   Inertia: {kmeans.inertia_:.2f}")
    return labels, centers

def extract_representatives(hashes: list[str], embeddings: np.ndarray, labels: np.ndarray, centers: np.ndarray, data: list[dict], n: int = CLUSTER_REPRESENTATIVES) -> list[dict]:  # Extract top-N representatives per cluster
    print(f"📌 Extracting {n} representatives per cluster...")
    clusters = []
    unique_labels = sorted(set(labels))
    
    for cluster_id in tqdm(unique_labels, desc="Clusters"):
        mask = labels == cluster_id
        cluster_hashes = np.array(hashes)[mask]
        cluster_embs = embeddings[mask]
        cluster_data = [d for d, m in zip(data, mask) if m]
        
        dists = np.linalg.norm(cluster_embs - centers[cluster_id], axis=1)  # Distance to center
        top_indices = np.argsort(dists)[:n]
        
        reps = [{"content_hash": cluster_hashes[i], "image_url": cluster_data[i]["image_url"], "category": cluster_data[i]["category"], "distance": float(dists[i])} for i in top_indices]
        clusters.append({"cluster_id": int(cluster_id), "size": int(mask.sum()), "center_embedding": centers[cluster_id].tolist(), "representatives": reps})
    
    return clusters

def save_clusters(clusters: list[dict], path=CLUSTERS_JSON):  # Save clusters to JSON
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f: json.dump(clusters, f, indent=2)
    print(f"💾 Saved {len(clusters)} clusters to {path}")

def update_db_clusters(hashes: list[str], labels: np.ndarray):  # Update cluster_id in Supabase
    print("📤 Updating cluster IDs in Supabase...")
    updates = list(zip(hashes, labels.tolist()))
    success = batch_update_clusters(updates)
    print(f"   Updated {success}/{len(updates)} records")

def run_clustering(k: int = DEFAULT_K, update_db: bool = True) -> list[dict]:  # Full clustering pipeline
    hashes, embeddings, data = load_embeddings()
    labels, centers = run_kmeans(embeddings, k)
    clusters = extract_representatives(hashes, embeddings, labels, centers, data)
    save_clusters(clusters)
    if update_db: update_db_clusters(hashes, labels)
    return clusters

def main():
    import argparse
    parser = argparse.ArgumentParser(description="K-means clustering")
    parser.add_argument("--k", type=int, default=DEFAULT_K, help=f"Number of clusters (default: {DEFAULT_K})")
    parser.add_argument("--no-db-update", action="store_true", help="Skip updating cluster_id in Supabase")
    args = parser.parse_args()
    run_clustering(k=args.k, update_db=not args.no_db_update)

if __name__ == "__main__":
    main()

