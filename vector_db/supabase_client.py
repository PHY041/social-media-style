import os, json # Supabase pgvector client for embedding storage
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(Path(__file__).parent.parent / ".env")  # Load .env from project root
_client: Optional[Client] = None

def get_client() -> Client:  # Lazy singleton client
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")  # Support both names
        if not url or not key: raise ValueError("Set SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        _client = create_client(url, key)
    return _client

def upsert_embedding(content_hash: str, image_url: str, category: str, category_type: str, search_term: str, title: str, alt_text: str, embedding: list[float]) -> bool:  # Insert or update embedding record
    try:
        get_client().table("image_embeddings").upsert({
            "content_hash": content_hash, "image_url": image_url, "category": category,
            "category_type": category_type, "search_term": search_term, "title": title or "",
            "alt_text": alt_text or "", "embedding": embedding
        }).execute()
        return True
    except Exception as e:
        print(f"⚠️ Supabase upsert failed: {e}")
        return False

def upsert_batch(records: list[dict], chunk_size: int = 10) -> int:  # Batch upsert with chunking for SSL stability
    success = 0
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        for attempt in range(3):  # Retry up to 3 times
            try:
                get_client().table("image_embeddings").upsert(chunk).execute()
                success += len(chunk)
                break
            except Exception as e:
                if attempt == 2: print(f"⚠️ Chunk {i//chunk_size} failed after 3 attempts: {e}")
                import time; time.sleep(1)  # Brief pause before retry
    return success

def search_similar(embedding: list[float], limit: int = 20) -> list[dict]:  # KNN search using pgvector
    result = get_client().rpc("match_embeddings", {"query_embedding": embedding, "match_count": limit}).execute()
    return result.data if result.data else []

def get_all_embeddings(batch_size: int = 500, min_aesthetic: float = None) -> list[dict]:  # Fetch all embeddings for clustering (paginated)
    from tqdm import tqdm
    all_data, offset = [], 0
    pbar = tqdm(desc="Fetching embeddings")
    while True:
        try:
            query = get_client().table("image_embeddings").select("content_hash,embedding,category,category_type,image_url,qalign_aesthetic")
            if min_aesthetic is not None:
                query = query.gte("qalign_aesthetic", min_aesthetic)
            result = query.range(offset, offset + batch_size - 1).execute()
            if not result.data: break
            all_data.extend(result.data)
            pbar.update(len(result.data))
            if len(result.data) < batch_size: break
            offset += batch_size
        except Exception as e:
            print(f"\n⚠️ Error at offset {offset}: {e}")
            if "timeout" in str(e).lower():
                print("   Retrying with smaller batch...")
                batch_size = max(100, batch_size // 2)
                continue
            break
    pbar.close()
    return all_data

def update_cluster_id(content_hash: str, cluster_id: int) -> bool:  # Update cluster assignment
    try:
        get_client().table("image_embeddings").update({"cluster_id": cluster_id}).eq("content_hash", content_hash).execute()
        return True
    except: return False

def batch_update_clusters(updates: list[tuple[str, int]]) -> int:  # Batch update cluster IDs
    success = 0
    for content_hash, cluster_id in updates:
        if update_cluster_id(content_hash, cluster_id): success += 1
    return success

# === SQL SETUP (run once in Supabase SQL editor) ===
SETUP_SQL = """
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table
CREATE TABLE IF NOT EXISTS image_embeddings (
    content_hash TEXT PRIMARY KEY,
    image_url TEXT NOT NULL,
    category TEXT,
    category_type TEXT,
    search_term TEXT,
    title TEXT,
    alt_text TEXT,
    embedding VECTOR(768),
    cluster_id INTEGER,
    source TEXT DEFAULT 'pinterest',       -- pinterest, behance, dribbble, adsoftheworld
    qalign_aesthetic FLOAT,                 -- Q-Align aesthetic score (0-5)
    qalign_quality FLOAT,                   -- Q-Align quality score (0-5)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add source column if table exists (migration)
-- ALTER TABLE image_embeddings ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'pinterest';
-- ALTER TABLE image_embeddings ADD COLUMN IF NOT EXISTS qalign_aesthetic FLOAT;
-- ALTER TABLE image_embeddings ADD COLUMN IF NOT EXISTS qalign_quality FLOAT;

-- Create vector index for similarity search
CREATE INDEX IF NOT EXISTS image_embeddings_embedding_idx 
ON image_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create function for similarity search
CREATE OR REPLACE FUNCTION match_embeddings(query_embedding VECTOR(768), match_count INT)
RETURNS TABLE (content_hash TEXT, image_url TEXT, category TEXT, category_type TEXT, similarity FLOAT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT ie.content_hash, ie.image_url, ie.category, ie.category_type,
           1 - (ie.embedding <=> query_embedding) AS similarity
    FROM image_embeddings ie
    ORDER BY ie.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
"""

