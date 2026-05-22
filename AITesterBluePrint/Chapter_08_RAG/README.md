---
title: VWO RAG System - Complete Setup Guide
author: AI Tester Blueprint
date: May 10, 2026
---

# 🎯 VWO RAG System - Complete Setup & Usage Guide

## ⚡ TL;DR - Quick Start (30 seconds)

```bash
# 1. Copy PDF to data folder
cp your_vwo_pdf.pdf ./data/

# 2. Ingest it
python chroma_rag_system.py

# 3. Open web interface
open rag_interface.html
# Paste API key: gsk_YOUR_GROQ_API_KEY_HERE

# 4. Start asking questions!
```

---

## 📦 What You Have

You now have a complete **RAG (Retrieval Augmented Generation)** system with:

### 🔧 Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **RAG Engine** | `chroma_rag_system.py` | Extract PDFs → Chunk → Embed → Store |
| **API Server** | `rag_api_server.py` | REST endpoints for programmatic access |
| **Web UI** | `rag_interface.html` | Beautiful interface for queries |
| **Vector DB** | ChromaDB (local) | Stores 384-dim embeddings |
| **Embeddings** | Nomic Embed | Free, open-source embedding model |
| **LLM** | Groq API | Fast Mixtral-8x7b inference |

### 📚 Documentation

| Document | Read When |
|----------|-----------|
| **This file** | Want a complete overview |
| `FINAL_SETUP_SUMMARY.md` | Need the summary |
| `QUICK_REFERENCE.md` | Need quick commands |
| `RAG_SETUP_GUIDE.md` | Want detailed instructions |
| `TROUBLESHOOTING.md` | Something isn't working |
| `ARCHITECTURE_DIAGRAMS.html` | Want visual diagrams |

---

## 🚀 Getting Started

### Step 1: Verify Everything is Installed

```bash
# Check Python
python --version
# Should be 3.8+

# Verify ChromaDB
python -c "import chromadb; print(f'ChromaDB: {chromadb.__version__}')"
# Output: ChromaDB: 1.5.9

# Verify Groq
python -c "import groq; print(f'Groq: {groq.__version__}')"
# Output: Groq: 1.2.0
```

### Step 2: Prepare Your PDF

```bash
# Copy your VWO requirements PDF to:
./data/vwo_requirements.pdf

# Or any other PDF:
./data/anything.pdf
```

**Important:** The PDF must be:
- ✅ Text-based (not image-only)
- ✅ In the `./data/` folder
- ✅ With `.pdf` extension

### Step 3: Ingest the PDF

```bash
python chroma_rag_system.py
```

**Expected output:**
```
✅ ChromaDB initialized at: ./chroma_db
📄 Extracted 45 pages from vwo_requirements.pdf
✂️  Split into 150 chunks
✅ Ingested 150 chunks from vwo_requirements.pdf
✅ Exported chunks data to chunks_data.json

📊 Collection Statistics:
   Total documents: 150
   Embeddings model: nomic-embed-text (Nomic AI)
```

This creates:
- `chroma_db/` - Vector database with embeddings
- `chunks_data.json` - Chunks data for visualization

### Step 4: Use the System

#### Option A: Web Interface (Easiest)

```bash
# Just open in browser:
# Windows: Double-click rag_interface.html
# Mac: open rag_interface.html
# Linux: xdg-open rag_interface.html

# Or in VS Code:
# Right-click rag_interface.html → Open Preview
```

Then:
1. Paste your Groq API key
2. Type a question
3. Click Search
4. See results!

#### Option B: API Server (For Backend Integration)

```bash
python rag_api_server.py
```

Then visit: `http://localhost:8000/docs`

You get interactive API documentation for all endpoints:
- `/search` - Search for chunks
- `/ingest` - Add new PDFs
- `/stats` - Get collection stats
- `/chunks` - Get all chunks

#### Option C: Python Code (For Automation)

```python
from chroma_rag_system import ChromaRAGSystem

# Initialize
rag = ChromaRAGSystem()

# Search
results = rag.search("What are VWO features?", top_k=5)
for result in results:
    print(f"[{result['rank']}] Similarity: {result['similarity']:.0%}")
    print(f"    {result['content'][:100]}...")

# Get stats
stats = rag.get_collection_stats()
print(f"Total chunks: {stats['total_documents']}")
```

---

## 🔍 Understanding the RAG Process

### Visual Pipeline

```
┌─────────────────────────────────────────────┐
│ YOUR VWO PDF                                │
│ (vwo_requirements.pdf)                      │
└──────────────┬──────────────────────────────┘
               │
               ▼ PyPDF2: Extract text
┌──────────────────────────────────────────────┐
│ RAW TEXT                                     │
│ (Thousands of words)                         │
└──────────────┬──────────────────────────────┘
               │
               ▼ RecursiveCharacterTextSplitter
┌──────────────────────────────────────────────┐
│ CHUNKS (150-200)                             │
│ Each chunk: ~1000 chars (200 words)          │
│ With 200-char overlap for continuity         │
└──────────────┬──────────────────────────────┘
               │
               ▼ Nomic Embed
┌──────────────────────────────────────────────┐
│ EMBEDDINGS (384-dimensional vectors)         │
│ Each chunk → Vector representation           │
│ (Mathematical representation of meaning)     │
└──────────────┬──────────────────────────────┘
               │
               ▼ ChromaDB Store
┌──────────────────────────────────────────────┐
│ VECTOR DATABASE (./chroma_db/)              │
│ - Vectors with indices                       │
│ - Metadata (source, chunk_index, etc)        │
│ - Ready for similarity search                │
└──────────────┬──────────────────────────────┘
               │
     ┌─────────┴─────────┐
     │                   │
     ▼                   ▼
┌─────────────┐    ┌──────────────┐
│ USER QUERY  │    │ VISUALIZATION│
│ "VWO        │    │ chunks_data  │
│  features?" │    │ .json        │
└──────┬──────┘    └──────────────┘
       │
       ▼ Embed query (same model)
┌──────────────────────────────────┐
│ QUERY VECTOR (384-dim)           │
└──────────────┬───────────────────┘
               │
               ▼ Cosine similarity search
┌──────────────────────────────────┐
│ TOP-5 CHUNKS                     │
│ [Sorted by similarity score]      │
└──────────────┬───────────────────┘
               │
               ▼ Format as context
┌──────────────────────────────────┐
│ CONTEXT FOR LLM                  │
│ Chunks + Query + System prompt    │
└──────────────┬───────────────────┘
               │
               ▼ Call Groq API
┌──────────────────────────────────┐
│ GROQ (Mixtral-8x7b)              │
│ - Fast inference (~100 tok/sec)   │
│ - 32K context window              │
│ - OpenGPT 1.20B model             │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│ AI-GENERATED ANSWER              │
│ Based on retrieved context        │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│ RESULTS DISPLAYED                │
│ - Retrieved chunks with scores    │
│ - AI answer                       │
│ - Source information              │
└──────────────────────────────────┘
```

### Key Concepts Explained

**Embeddings**: Convert text to numbers
- VWO PDF → 384 numbers per chunk
- These numbers capture the *meaning*
- Similar meanings = similar numbers

**Semantic Search**: Find by meaning, not keywords
- Not keyword matching
- Uses cosine similarity (0-1 scale)
- "VWO features" matches "capabilities" too

**Context Window**: How much the LLM sees
- Mixtral-8x7b: 32,768 tokens max
- We send: Top 5 chunks + query
- LLM generates: Informed response

**RAG vs Pure LLM**:
- Pure LLM: "Tell me about VWO"
  - Uses training data only (may be outdated)
  - Hallucination risk
  
- RAG: "Tell me about VWO based on this doc"
  - Uses current documentation
  - Grounded in real data
  - More accurate

---

## 📊 Examples

### Example 1: Basic Query

```
User Query: "What is VWO?"

System:
1. Embeds query to 384-dim vector
2. Searches ChromaDB for similar chunks
3. Finds top 5 chunks:
   - "VWO is a Visual Website Optimizer..." (85% match)
   - "VWO enables A/B testing..." (82% match)
   - "VWO supports personalization..." (78% match)
   - "VWO integrates with analytics..." (72% match)
   - "VWO provides conversion tracking..." (70% match)

4. Sends to Groq with context
5. Groq generates:
   "VWO (Visual Website Optimizer) is a platform for A/B testing 
    and personalization. It enables website optimization through 
    experimentation and data-driven personalization..."

Result: Accurate, sourced answer!
```

### Example 2: Detailed Query

```
User Query: "How do I set up an A/B test in VWO?"

Top Retrieved Chunks:
1. "To set up an A/B test: 1) Create experiment 2) Define variations..."
2. "A/B testing best practices: Set minimum sample size..."
3. "VWO's A/B test reporting shows statistical significance..."
4. "Variations can include text, images, or layout changes..."
5. "Target your A/B test to specific audience segments..."

Groq Response:
"Setting up an A/B test in VWO involves several steps:
1. Create a new experiment...
2. Define your variations...
3. Set targeting rules...
4. Configure success metrics...
5. Launch and monitor..."

Much better than generic response!
```

---

## ⚙️ Configuration

### Chunking Strategy (in `chroma_rag_system.py`)

```python
# Edit these for different behavior
chunk_size = 1000          # Characters per chunk
chunk_overlap = 200        # Overlap between chunks

# Smaller chunks = more chunks, faster processing
# Larger chunks = better context, fewer chunks
# More overlap = better context continuity
```

### Search Results (in `rag_interface.html`)

```javascript
// Edit these for different behavior
const topK = 5;            // Number of results to retrieve

// Fewer = faster and cheaper
// More = potentially better answers
```

### LLM Temperature (advanced)

```python
# In rag_api_server.py (if adding direct LLM calls)
temperature = 0.7          # Randomness (0.0 = deterministic, 1.0 = random)

# Lower = more consistent
# Higher = more creative
```

---

## 🔑 Your API Key

```
Groq API Key: gsk_YOUR_GROQ_API_KEY_HERE

Model: Mixtral-8x7b-32768
Context: 32,768 tokens
Speed: ~100 tokens/second
Cost: Very affordable
```

**Keep this key secure!** It's what enables AI responses.

---

## 📈 Performance Expectations

| Metric | Value | Notes |
|--------|-------|-------|
| PDF Ingestion | <30 sec | Per 100-page PDF |
| Chunk Generation | <5 sec | 150 chunks from 100 pages |
| Embedding Generation | <10 sec | All 150 chunks |
| Search Latency | <100ms | Local ChromaDB, no network |
| Groq API Response | 1-3 sec | Depends on response length |
| Total Query Time | 2-5 sec | Search + LLM generation |

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "No PDFs found" | Copy PDF to ./data/ folder |
| ChromaDB connection error | Delete chroma_db/ and re-run ingestion |
| Groq API error | Check API key in browser console |
| Slow search | Reduce chunk size or number of documents |
| Memory error | Process PDFs one at a time |
| CORS error | Start API server instead of file:// |

**For more:** See `TROUBLESHOOTING.md`

---

## 🎓 Learning Outcomes

Using this system, you now understand:

1. **Document Processing**
   - PDF extraction and parsing
   - Intelligent text chunking
   - Metadata preservation

2. **Embeddings & Vectors**
   - Converting text to high-dimensional vectors
   - Semantic similarity computation
   - Vector space properties

3. **Vector Databases**
   - Storing embeddings efficiently
   - Similarity-based retrieval
   - Indexing strategies

4. **RAG Architecture**
   - Combining retrieval with generation
   - Context window management
   - Prompt engineering basics

5. **API Integration**
   - Building REST endpoints
   - Error handling
   - Rate limiting considerations

6. **Full-Stack Development**
   - Frontend (HTML/JavaScript)
   - Backend (Python/FastAPI)
   - Database (ChromaDB)
   - External APIs (Groq)

---

## 🚀 Next Steps

### Immediate (This Hour)
1. ✅ Copy your VWO PDF to ./data/
2. ✅ Run: `python chroma_rag_system.py`
3. ✅ Open: `rag_interface.html`
4. ✅ Ask your first question!

### Short Term (This Week)
- Add multiple PDFs to ./data/
- Experiment with different queries
- Try different chunk sizes
- Share with team members

### Medium Term (This Month)
- Deploy API server to cloud
- Build custom UI for your app
- Integrate with other systems
- Add more document types

### Long Term (This Quarter)
- Scale to large document sets
- Add real-time updates
- Implement caching
- Add multi-user support

---

## 📞 Support Matrix

| Need | Go To | Time |
|------|-------|------|
| Quick command | `QUICK_REFERENCE.md` | <5 min |
| How to set up | `RAG_SETUP_GUIDE.md` | 15 min |
| Something broken | `TROUBLESHOOTING.md` | 20 min |
| Visual explanation | `ARCHITECTURE_DIAGRAMS.html` | 10 min |
| API documentation | `http://localhost:8000/docs` | 5 min |

---

## ✅ Checklist

Before you start, verify:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (ChromaDB, Groq, etc.)
- [ ] data/ folder exists
- [ ] chroma_db/ folder created
- [ ] chunks_data.json generated (after ingestion)
- [ ] Groq API key ready
- [ ] PDF copied to ./data/
- [ ] rag_interface.html opens in browser

---

## 🎉 You're All Set!

Your complete **VWO RAG System** is ready to use!

```bash
# Start here:
python chroma_rag_system.py
open rag_interface.html
```

Then ask questions and get AI-powered answers based on your VWO documentation!

---

## 📚 Quick File Reference

```
chroma_rag_system.py       ← Start: PDF ingestion
rag_interface.html         ← Start: Web interface
rag_api_server.py          ← Advanced: REST API
setup.py                   ← Already run: Setup
FINAL_SETUP_SUMMARY.md     ← Read: Complete overview
QUICK_REFERENCE.md         ← Read: Common commands
RAG_SETUP_GUIDE.md         ← Read: Detailed guide
TROUBLESHOOTING.md         ← Read: When stuck
ARCHITECTURE_DIAGRAMS.html ← View: Visual diagrams
```

---

**Happy RAGing! 🚀**

*Created: May 10, 2026*
*Technology: ChromaDB + Nomic Embed + Groq + FastAPI*
*Status: ✅ Ready to use*
