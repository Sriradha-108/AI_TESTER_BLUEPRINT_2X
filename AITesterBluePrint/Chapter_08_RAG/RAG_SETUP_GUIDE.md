# VWO RAG System - Complete Setup Guide

## 📋 Overview

This is a complete **Retrieval Augmented Generation (RAG)** system that combines:
- **ChromaDB**: Local vector database for semantic search
- **Nomic Embed**: Free, open-source embedding model (384-dimensional vectors)
- **Groq API**: Fast LLM inference with Mixtral-8x7b model
- **Beautiful HTML Interface**: Interactive query interface with visualization

## 🎯 What You Get

1. **Folder Structure**
   ```
   Chapter_08_RAG/
   ├── data/                      # 📂 Place your VWO PDF here
   ├── chroma_db/                 # 🗄️ ChromaDB persistent storage
   ├── chroma_rag_system.py       # 🐍 Core RAG logic
   ├── rag_api_server.py          # 🚀 FastAPI server
   ├── rag_interface.html         # 🌐 Web interface
   ├── chunks_data.json           # 📊 Chunks visualization data
   └── requirements_chroma_rag.txt # 📦 Dependencies
   ```

2. **Chunk Visualization**: See exactly which parts of the PDF were extracted and how they're stored

3. **Semantic Search**: Query the chunks and get the most relevant ones based on meaning (not just keywords)

4. **Groq Integration**: Get AI-generated answers using context from the most relevant chunks

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements_chroma_rag.txt
```

### Step 2: Place Your VWO PDF
```
Copy your VWO product requirements PDF to: ./data/vwo_requirements.pdf
```

### Step 3: Ingest the PDF into ChromaDB
```bash
python chroma_rag_system.py
```

This will:
- Extract text from all PDFs in the `./data` folder
- Split them into chunks (1000 chars, 200 char overlap)
- Generate embeddings using Nomic Embed
- Store in local ChromaDB
- Generate `chunks_data.json` for visualization

### Step 4: Open the Web Interface
```bash
# Open in your browser:
file:///path/to/rag_interface.html
```

Or start the API server:
```bash
python rag_api_server.py
# Then visit: http://localhost:8000/docs
```

### Step 5: Query with Groq
1. Paste your Groq API key in the interface
2. Enter a question about VWO product requirements
3. See the retrieved chunks and AI-generated answer

## 🔑 API Key Setup

### Get your Groq API Key:
1. Visit: https://console.groq.com
2. Sign up / Login
3. Generate an API key
4. Paste it in the HTML interface

Your key: `gsk_YOUR_GROQ_API_KEY_HERE`

## 📊 System Architecture

```
┌─────────────┐
│ PDF Files   │  (./data/*.pdf)
└──────┬──────┘
       │ Extract Text
       ▼
┌──────────────────────────────┐
│ RecursiveCharacterSplitter   │  (1000 chars, 200 overlap)
└──────┬───────────────────────┘
       │ Create Chunks
       ▼
┌──────────────────────────────┐
│ Nomic Embed (384-dim vectors)│  (Free, Open-source)
└──────┬───────────────────────┘
       │ Generate Embeddings
       ▼
┌──────────────────────────────┐
│ ChromaDB (Local Storage)      │  (./chroma_db/)
│ - Vector Index               │
│ - Metadata Store             │
└──────┬───────────────────────┘
       │
       ├──────────────────────────┐
       │                          │
       ▼                          ▼
┌─────────────────┐    ┌──────────────────────┐
│ User Query      │    │ chunks_data.json     │
│ (Web Interface) │    │ (Visualization)      │
└────────┬────────┘    └──────────────────────┘
         │
         │ 1. Embed Query (Nomic Embed)
         │ 2. Search (Cosine Similarity)
         ▼
┌──────────────────────────────┐
│ Top-K Similar Chunks         │  (Cosine Similarity Search)
│ (with similarity scores)      │
└──────┬───────────────────────┘
       │ Format as Context
       ▼
┌──────────────────────────────┐
│ Groq API (Mixtral-8x7b)      │  (Fast LLM Inference)
│ OpenGPT 1.20B Model          │
└──────┬───────────────────────┘
       │ Generate Response
       ▼
┌──────────────────────────────┐
│ AI-Generated Answer          │
│ + Retrieved Chunks Display   │
└──────────────────────────────┘
```

## 📚 File Descriptions

### 1. `chroma_rag_system.py` - Core RAG Engine
- **`ChromaRAGSystem` class**: Main RAG engine
- **Methods**:
  - `extract_text_from_pdf()`: Extract text using PyPDF2
  - `chunk_text()`: Split using RecursiveCharacterTextSplitter
  - `ingest_pdf()`: Process and store in ChromaDB
  - `search()`: Semantic search with cosine similarity
  - `export_chunks_for_visualization()`: Generate JSON for UI

### 2. `rag_api_server.py` - FastAPI Backend
- **Endpoints**:
  - `POST /search`: Search ChromaDB
  - `POST /ingest`: Ingest new PDF
  - `GET /stats`: Collection statistics
  - `GET /chunks`: Get all chunks
  - `GET /list-pdfs`: List PDFs in data folder
  - `GET /health`: Health check

### 3. `rag_interface.html` - Web Interface
- **Features**:
  - 📚 Left panel: Shows all extracted chunks
  - 🚀 Right panel: Query interface + Groq integration
  - 📊 Diagram: RAG flow visualization
  - 🗄️ Database: Vector space visualization
  - 📈 Stats: Total chunks, sources, embedding dimensions

### 4. `chunks_data.json` - Visualization Data
Generated automatically after running `chroma_rag_system.py`
```json
{
  "metadata": {
    "total_documents": 150,
    "collection_name": "vwo_app_docs",
    "embeddings_model": "nomic-embed-text"
  },
  "chunks": [
    {
      "id": "vwo_requirements_chunk_0",
      "source": "vwo_requirements.pdf",
      "chunk_index": 0,
      "content": "VWO is a visual website optimizer...",
      "length": 1024
    },
    ...
  ]
}
```

## 🧬 Embedding Model Details

### Nomic Embed (Free & Open Source)
- **Model**: `nomic-embed-text`
- **Dimensions**: 384-dimensional vectors
- **Characteristics**:
  - Fast inference
  - Free tier available
  - No API key required (offline use available)
  - Excellent semantic understanding
  - Optimized for long documents

## 🤖 LLM Model Details

### Groq Mixtral-8x7b
- **Model**: `mixtral-8x7b-32768`
- **Context Window**: 32,768 tokens
- **Speed**: ~100 tokens/sec
- **Cost**: Very affordable compared to GPT-4
- **Quality**: Good balance of quality and speed

## 📈 Query Flow Example

```
User Query: "What are VWO's main features?"

Step 1: Embed Query
  Query Text → Nomic Embed → [0.12, 0.45, -0.23, ..., 0.78] (384 dims)

Step 2: Search ChromaDB
  Cosine Similarity between query vector and all chunk vectors
  
  Chunk 1: "VWO allows A/B testing, personalization..." → Similarity: 89%
  Chunk 2: "VWO is a conversion rate optimization..." → Similarity: 75%
  Chunk 3: "VWO integrates with analytics tools..." → Similarity: 62%
  (Top 5 retrieved with similarity scores)

Step 3: Build Context
  Context = Top 3 chunks + Source info + Similarity scores

Step 4: Call Groq API
  System Prompt: "You are a VWO expert..."
  Context: [Retrieved chunks]
  Query: "What are VWO's main features?"
  → Response from Mixtral-8x7b

Step 5: Display Results
  - Show retrieved chunks with similarity %
  - Show Groq's AI-generated answer
  - Show which PDF each chunk came from
```

## 🔍 Advanced Usage

### Custom Chunking Parameters
Edit `chroma_rag_system.py`:
```python
def chunk_text(self, text, chunk_size=1000, chunk_overlap=200):
    # Increase chunk_size for longer context
    # Increase chunk_overlap for more connectivity
```

### Multiple PDFs
Just place multiple PDFs in `./data/`:
```
./data/
├── vwo_requirements.pdf
├── vwo_api_docs.pdf
├── vwo_best_practices.pdf
```

Then run: `python chroma_rag_system.py`

### Using the API Server
```bash
# Start server
python rag_api_server.py

# Search via curl
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "VWO features", "top_k": 5}'

# Ingest PDF
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "./data/vwo.pdf", "source_name": "vwo_requirements"}'
```

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'chromadb'"
**Solution**: 
```bash
pip install -r requirements_chroma_rag.txt
```

### Issue: "No PDFs found in data folder"
**Solution**: 
```bash
# Create data folder and add PDF
mkdir -p ./data
cp /path/to/your/vwo_requirements.pdf ./data/
python chroma_rag_system.py
```

### Issue: "Groq API Error: Invalid API key"
**Solution**:
1. Check API key at https://console.groq.com
2. Ensure key is copied correctly (gsk_...)
3. Paste in HTML interface

### Issue: "CORS error when accessing from HTML"
**Solution**:
Start the API server:
```bash
python rag_api_server.py
```

## 📊 Visualization Features

### Chunks Panel (Left)
- Shows each chunk extracted from PDFs
- Displays first 200 chars of content
- Shows source PDF name
- Interactive hover effects

### Query Panel (Right)
- Enter Groq API key
- Set number of results (3, 5, or 10)
- Enter your question
- See retrieved chunks with similarity scores
- View Groq's AI response

### Diagram Section
- **RAG Flow**: Visual pipeline from query to response
- **Vector Space**: Shows all chunks as vectors
- **Database Stats**: Total documents, sources, embedding dimensions
- **Detailed Workflow**: 9-step breakdown of the RAG process

## 🎓 Learning Outcomes

After using this system, you'll understand:
1. ✅ How RAG systems work (Retrieval + Augmented Generation)
2. ✅ Document chunking strategies
3. ✅ Embedding generation and vector similarity
4. ✅ Vector database operations
5. ✅ LLM context window usage
6. ✅ API integration patterns
7. ✅ Full-stack system architecture

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| chromadb | 0.4.24 | Vector database |
| PyPDF2 | 3.0.1 | PDF extraction |
| nomic | 1.1.2 | Embedding model |
| langchain | 0.2.1 | Text utilities |
| groq | 0.9.0 | LLM API client |
| fastapi | Latest | API server |
| uvicorn | Latest | ASGI server |

## 🚀 Next Steps

1. ✅ Install dependencies
2. ✅ Add your VWO PDF to `./data/`
3. ✅ Run `python chroma_rag_system.py`
4. ✅ Open `rag_interface.html` in browser
5. ✅ Enter Groq API key
6. ✅ Ask questions!

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all dependencies are installed
3. Ensure PDF is in `./data/` folder
4. Check Groq API key validity

---

**Happy RAGing! 🚀**
