from pydantic import BaseModel, Field # API request/response schemas
from typing import Optional

class TextSearchRequest(BaseModel): # POST /search/text
    query: str = Field(..., min_length=1, max_length=500)
    k: int = Field(20, ge=1, le=100)
    filters: Optional[dict] = None

class ImageResult(BaseModel): # Single image result
    content_hash: str
    image_url: str
    category: str
    category_type: str
    similarity: float

class SearchResponse(BaseModel): # Search response
    query: str
    count: int
    results: list[ImageResult]

class ClusterSummary(BaseModel): # Cluster list item
    cluster_id: int
    size: int
    top_categories: list[str]

class ClusterDetail(BaseModel): # Full cluster detail
    cluster_id: int
    size: int
    representatives: list[dict]

class StatsResponse(BaseModel): # GET /stats
    total_images: int
    total_clusters: int
    category_distribution: dict[str, int]
