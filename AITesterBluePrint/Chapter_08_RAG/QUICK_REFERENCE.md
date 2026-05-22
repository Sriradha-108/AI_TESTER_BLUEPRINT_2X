# VWO RAG System - Quick Reference Card

## 🚀 Quick Start Commands

```bash
# 1. Install everything
python setup.py

# 2. Add your PDF to data folder
cp /path/to/vwo_requirements.pdf ./data/

# 3. Ingest the PDF
python chroma_rag_system.py

# 4. Open the interface
# Windows: start rag_interface.html
# Mac: open rag_interface.html
# Linux: xdg-open rag_interface.html

# 5. (Optional) Start API server
python rag_api_server.py
# Then visit: http://localhost:8000/docs
```

## 📁 File Structure

| File | Purpose | Key Class/Function |
|------|---------|-------------------|
| `chroma_rag_system.py` | Core RAG engine | `ChromaRAGSystem` |
| `rag_api_server.py` | FastAPI REST API | `app`, `/search`, `/ingest` |
| `rag_interface.html` | Web UI & visualization | `performSearch()`, `loadChunksData()` |
| `setup.py` | Automated setup | `setup_rag_system()` |
| `chunks_data.json` | Generated chunks data | (auto-generated) |

## 🔧 Configuration

### Chunking Parameters (edit `chroma_rag_system.py`)
```python
chunk_size=1000      # Characters per chunk
chunk_overlap=200    # Overlap between chunks
```

### Search Results (edit `rag_interface.html`)
```javascript
const topK = 5;      // Number of results to retrieve
```

### ChromaDB Settings (edit `chroma_rag_system.py`)
```python
ChromaClient(settings)
# Automatically uses cosine similarity (best for embeddings)
```

## 🔑 API Keys & Credentials

| Service | Key Type | Obtained From | Used In |
|---------|----------|---------------|---------|
| Groq | Bearer Token | https://console.groq.com | `rag_interface.html` |
| Nomic Embed | None (free, local) | Included in package | `chroma_rag_system.py` |
| ChromaDB | None (local) | Included in package | `chroma_rag_system.py` |

**Your Groq API Key:**
```
gsk_YOUR_GROQ_API_KEY_HERE
```

## 📊 Data Flow Summary

```
PDF → Extract → Chunk → Embed → Store (ChromaDB)
                                    ↓
                         Query → Embed → Search
                                    ↓
                         Top-K Results → Context → Groq → Response
```

## 🔍 Important Functions

### `chroma_rag_system.py`

```python
# Initialize RAG system
rag = ChromaRAGSystem(persist_dir="./chroma_db", data_dir="./data")

# Ingest a PDF
rag.ingest_pdf("./data/vwo.pdf", source_name="vwo_requirements")

# Search for chunks
results = rag.search("What are VWO features?", top_k=5)

# Get statistics
stats = rag.get_collection_stats()

# Export for visualization
rag.export_chunks_for_visualization("chunks_data.json")
```

### `rag_interface.html`

```javascript
// Load chunks from JSON
loadChunksData()

// Perform semantic search
performSearch()

// Get Groq response
getGroqResponse(query, context, apiKey)

// Render chunks
renderChunks(chunks)

// Display results
displayRetrievalResults(results)
displayAIResponse(response)
```

## 📈 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Embedding Dim | 384 | Nomic Embed output |
| Max Chunk Size | 1000 chars | ~200 words |
| Chunk Overlap | 200 chars | Maintains context |
| Similarity Metric | Cosine | Best for embeddings |
| LLM Context Window | 32,768 tokens | Mixtral-8x7b |
| LLM Speed | ~100 tokens/sec | Groq advantage |
| Search Latency | <100ms | Local ChromaDB |
| Total System Latency | 1-3 seconds | Including LLM |

## 🐛 Troubleshooting Checklist

```
[ ] Python 3.8+ installed?
[ ] requirements_chroma_rag.txt installed?
[ ] data/ folder exists?
[ ] PDF copied to data/ folder?
[ ] chroma_rag_system.py ran successfully?
[ ] chunks_data.json created?
[ ] rag_interface.html opens in browser?
[ ] Groq API key is valid?
[ ] Network connection active?
[ ] No firewall blocking API calls?
```

## 🎯 Common Tasks

### Add a new PDF
```bash
# 1. Copy PDF to data folder
cp new_doc.pdf ./data/

# 2. Re-run ingestion
python chroma_rag_system.py

# 3. Refresh browser
```

### Modify chunking strategy
```python
# Edit chroma_rag_system.py
chunks = self.chunk_text(
    text,
    chunk_size=2000,      # Larger chunks
    chunk_overlap=500     # More overlap
)
```

### Clear all data and restart
```bash
# 1. Delete ChromaDB
rm -rf chroma_db/        # Linux/Mac
rmdir /s chroma_db       # Windows

# 2. Run setup again
python setup.py

# 3. Add PDF and reingest
python chroma_rag_system.py
```

### Use API server instead of HTML
```bash
# 1. Start server
python rag_api_server.py

# 2. Search via API
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "VWO features", "top_k": 5}'

# 3. View docs
open http://localhost:8000/docs
```

## 📚 Key Concepts

| Term | Definition | In This System |
|------|-----------|-----------------|
| RAG | Retrieval + Augmented Generation | PDF → Search → LLM |
| Embedding | Vector representation of text | 384-dimensional |
| Vector DB | Database for vector similarity | ChromaDB |
| Semantic Search | Meaning-based, not keyword | Cosine similarity |
| Chunking | Splitting docs into pieces | RecursiveCharacterTextSplitter |
| Context Window | Max tokens LLM can see | 32,768 for Mixtral |
| Temperature | LLM randomness (0-1) | 0.7 default |

## 🚨 Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: chromadb` | Dependency not installed | `pip install chromadb` |
| `No PDFs found in ./data` | Folder empty | Copy PDF to ./data/ |
| `Invalid API key` | Wrong Groq key | Check https://console.groq.com |
| `CORS error` | HTML → API call blocked | Use API server instead |
| `ChromaDB already exists` | Rerunning ingestion | Delete ./chroma_db/ first |
| `Connection refused: localhost:8000` | API server not running | `python rag_api_server.py` |

## 📞 Support Resources

| Resource | URL/Location | Use For |
|----------|-------------|---------|
| Full Guide | `RAG_SETUP_GUIDE.md` | Detailed instructions |
| Architecture | `ARCHITECTURE_DIAGRAMS.html` | Visual diagrams |
| API Docs | `http://localhost:8000/docs` | API endpoints |
| Code Docs | File docstrings | Implementation details |
| Setup Script | `setup.py` | Automated setup |

## 💡 Pro Tips

1. **Faster ingestion**: Use smaller chunks for large PDFs
   ```python
   chunk_size=500  # Faster processing
   ```

2. **Better retrieval**: Increase overlap for more context
   ```python
   chunk_overlap=300  # More context overlap
   ```

3. **Cheaper Groq usage**: Fewer results means less processing
   ```javascript
   const topK = 3;  // Default top-3 instead of top-5
   ```

4. **Better answers**: More chunks = better context
   ```javascript
   const topK = 10;  # More context, potentially better answers
   ```

5. **Persistent storage**: ChromaDB saves locally, no re-ingestion needed
   - Just restart your app, data is still there
   - Backup: `zip -r chroma_db_backup.zip chroma_db/`

---

**For more help, see RAG_SETUP_GUIDE.md** 📖
