from fastapi import APIRouter, HTTPException # Search endpoints
import sys; sys.path.insert(0, str(__file__).rsplit("/", 3)[0])
from api.schemas import TextSearchRequest, SearchResponse, ImageResult
from api.embed_service import get_text_embedding
from vector_db.supabase_client import search_similar

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/text", response_model=SearchResponse)
async def search_by_text(req: TextSearchRequest):
    """Text-to-image similarity search"""
    try:
        emb = get_text_embedding(req.query)
        raw = search_similar(emb, limit=req.k)
        results = [ImageResult(content_hash=r["content_hash"], image_url=r["image_url"], category=r["category"], category_type=r["category_type"], similarity=r["similarity"]) for r in raw]
        return SearchResponse(query=req.query, count=len(results), results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

