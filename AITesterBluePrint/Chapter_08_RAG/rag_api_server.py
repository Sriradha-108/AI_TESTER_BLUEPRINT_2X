"""
ChromaDB RAG Backend API
Provides REST endpoints for RAG system with ChromaDB + Nomic Embed + Groq
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import json
from chroma_rag_system import ChromaRAGSystem

# Load environment variables
load_dotenv()

app = FastAPI(title="ChromaDB RAG API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = ChromaRAGSystem(
    persist_dir="./chroma_db",
    data_dir="./data"
)

# Request/Response models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    rank: int
    content: str
    source: str
    chunk_index: int
    distance: float
    similarity: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_found: int

class IngestionRequest(BaseModel):
    pdf_path: str
    source_name: Optional[str] = None

class CollectionStats(BaseModel):
    total_documents: int
    collection_name: str
    embeddings_model: str

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ChromaDB RAG API"
    }

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search for relevant chunks in the ChromaDB
    """
    try:
        results = rag_system.search(request.query, top_k=request.top_k)
        return SearchResponse(
            query=request.query,
            results=[SearchResult(**r) for r in results],
            total_found=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_pdf(request: IngestionRequest):
    """
    Ingest a PDF file into ChromaDB
    """
    try:
        chunks_count = rag_system.ingest_pdf(
            request.pdf_path,
            source_name=request.source_name
        )
        
        # Export updated chunks
        rag_system.export_chunks_for_visualization("chunks_data.json")
        
        return {
            "status": "success",
            "message": f"Ingested {chunks_count} chunks",
            "chunks_count": chunks_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=CollectionStats)
async def get_stats():
    """
    Get collection statistics
    """
    try:
        stats = rag_system.get_collection_stats()
        return CollectionStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-pdfs")
async def list_pdfs():
    """
    List all PDFs in the data folder
    """
    try:
        files = rag_system.list_files_in_data_folder()
        return {
            "pdfs": files,
            "count": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chunks")
async def get_all_chunks():
    """
    Get all chunks metadata for visualization
    """
    try:
        with open("chunks_data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chunks data not found. Please ingest a PDF first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ChromaDB RAG API Server...")
    print("📍 API available at: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
