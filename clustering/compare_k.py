import sys # Compare K values using silhouette score and inertia
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from embedding.config_embed import K_CANDIDATES
from clustering.kmeans_cluster import load_embeddings

def compare_k_values(embeddings: np.ndarray, k_values: list[int] = K_CANDIDATES) -> dict:  # Run K-means for each K and compute metrics
    print(f"🔍 Comparing K values: {k_values}")
    results = {}
    
    for k in k_values:
        print(f"\n   K={k}...")
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
        labels = kmeans.fit_predict(embeddings)
        
        sil = silhouette_score(embeddings, labels, sample_size=min(10000, len(embeddings)))  # Sample for speed
        results[k] = {"inertia": float(kmeans.inertia_), "silhouette": float(sil), "labels": labels}
        print(f"      Inertia: {kmeans.inertia_:.2f}, Silhouette: {sil:.4f}")
    
    return results

def print_report(results: dict):  # Print comparison report
    print("\n" + "="*60)
    print("📊 K-VALUE COMPARISON REPORT")
    print("="*60)
    print(f"{'K':<10} {'Inertia':<15} {'Silhouette':<12} {'Recommendation'}")
    print("-"*60)
    
    best_sil_k = max(results.keys(), key=lambda k: results[k]["silhouette"])
    for k in sorted(results.keys()):
        r = results[k]
        rec = "⭐ BEST" if k == best_sil_k else ""
        print(f"{k:<10} {r['inertia']:<15.2f} {r['silhouette']:<12.4f} {rec}")
    
    print("-"*60)
    print(f"💡 Recommendation: K={best_sil_k} has highest silhouette score")
    print("="*60)

def main():
    _, embeddings, _ = load_embeddings()
    results = compare_k_values(embeddings)
    print_report(results)

if __name__ == "__main__":
    main()



