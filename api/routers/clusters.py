from fastapi import APIRouter, HTTPException # Cluster endpoints
import sys; sys.path.insert(0, str(__file__).rsplit("/", 3)[0])
from api.schemas import ClusterSummary, ClusterDetail
from api.cluster_service import get_all_clusters, get_cluster_by_id

router = APIRouter(prefix="/clusters", tags=["clusters"])

@router.get("", response_model=list[ClusterSummary])
async def list_clusters():
    """List all clusters with summary info"""
    try:
        clusters = get_all_clusters()
        return [ClusterSummary(cluster_id=c["cluster_id"], size=c["size"], top_categories=c["top_categories"]) for c in clusters]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{cluster_id}", response_model=ClusterDetail)
async def get_cluster(cluster_id: int):
    """Get detailed info for a specific cluster"""
    try:
        cluster = get_cluster_by_id(cluster_id)
        if not cluster: raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")
        return ClusterDetail(cluster_id=cluster["cluster_id"], size=cluster["size"], representatives=cluster["representatives"])
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

