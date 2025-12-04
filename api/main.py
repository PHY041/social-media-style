from fastapi import FastAPI # Style Universe API - Visual Intelligence Service
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import sys; sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from api.routers import search, clusters
from api.schemas import StatsResponse
from api.cluster_service import get_stats

app = FastAPI(title="Style Universe API", description="Visual style embedding search & clustering service", version="1.0.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(search.router)
app.include_router(clusters.router)

FRONTEND_DIR = Path(__file__).parent / "frontend"
if FRONTEND_DIR.exists(): app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def root():
    """Serve frontend or redirect to docs"""
    index = FRONTEND_DIR / "index.html"
    return FileResponse(index) if index.exists() else {"message": "Style Universe API", "docs": "/docs"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "style-universe"}

@app.get("/stats", response_model=StatsResponse)
async def stats():
    """Get dataset statistics"""
    try:
        data = get_stats()
        return StatsResponse(total_images=data["total_images"], total_clusters=data["total_clusters"], category_distribution=data["category_distribution"])
    except: return StatsResponse(total_images=0, total_clusters=0, category_distribution={})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
