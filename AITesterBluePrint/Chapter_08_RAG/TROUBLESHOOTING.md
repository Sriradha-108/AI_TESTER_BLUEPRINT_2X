# VWO RAG System - Troubleshooting Guide

## 🔍 Common Issues & Solutions

### ❌ Installation Issues

#### Issue: `pip install` fails
**Symptoms:** Error messages during dependency installation

**Solutions:**
```bash
# 1. Upgrade pip first
python -m pip install --upgrade pip

# 2. Install with verbose output
pip install -r requirements_chroma_rag.txt -v

# 3. Install one by one
pip install chromadb==0.4.24
pip install PyPDF2==3.0.1
pip install nomic==1.1.2
# ... etc

# 4. Use Python 3.9+ if available
python3.9 -m pip install -r requirements_chroma_rag.txt
```

#### Issue: `No module named 'chromadb'`
**Symptoms:** ModuleNotFoundError when running scripts

**Solutions:**
```bash
# Verify installation
python -c "import chromadb; print(chromadb.__version__)"

# Reinstall if not found
pip uninstall chromadb -y && pip install chromadb==0.4.24

# Check Python path
which python
# Make sure it's using the right Python environment
```

#### Issue: Python 3.7 or older
**Symptoms:** Compatibility errors, syntax issues

**Solutions:**
```bash
# Check Python version
python --version

# Install Python 3.8+ from:
# https://www.python.org/downloads/

# Or use pyenv/conda:
brew install python@3.11
/usr/local/opt/python@3.11/bin/python3.11 -m pip install -r requirements_chroma_rag.txt
```

---

### ❌ PDF Ingestion Issues

#### Issue: "No PDFs found in ./data"
**Symptoms:** Script runs but finds no PDFs to ingest

**Solutions:**
```bash
# 1. Verify data folder exists
ls -la data/
# OR (Windows)
dir data

# 2. Check PDF is in correct location
# Should be: ./data/filename.pdf
# NOT: ./data/subfolder/filename.pdf

# 3. Verify PDF filename ends with .pdf
ls -la data/*.pdf

# 4. Manually ingest if needed
python -c "
from chroma_rag_system import ChromaRAGSystem
rag = ChromaRAGSystem()
rag.ingest_pdf('./data/your_pdf.pdf', 'your_source_name')
"
```

#### Issue: "Error reading PDF: [error message]"
**Symptoms:** PDF extraction fails with error

**Solutions:**
```bash
# 1. Verify PDF is not corrupted
file data/your_pdf.pdf
# Should show: PDF document

# 2. Try with different PDF
cp /path/to/another/pdf.pdf ./data/test.pdf
python chroma_rag_system.py

# 3. Check PDF permissions
chmod 644 data/*.pdf

# 4. Try re-downloading the PDF
# The PDF might be corrupted during download
```

#### Issue: "PDF text extraction is empty"
**Symptoms:** PDF processed but contains no text (image-only PDF)

**Solutions:**
```bash
# This system only works with text-based PDFs
# For image-based PDFs, you need OCR:

# Install pytesseract
pip install pytesseract pillow pdf2image

# Then process image-based PDFs manually
# (This is advanced - use text PDFs for now)
```

---

### ❌ ChromaDB Issues

#### Issue: "ChromaDB already exists" error on re-run
**Symptoms:** Error when running ingestion script twice

**Solutions:**
```bash
# Option 1: Delete and restart
rm -rf chroma_db/              # Linux/Mac
rmdir /s /q chroma_db         # Windows
python chroma_rag_system.py

# Option 2: Use new collection name
# Edit chroma_rag_system.py and change collection name

# Option 3: Just continue (safe to re-ingest)
# ChromaDB will skip duplicates by default
python chroma_rag_system.py   # Just run again
```

#### Issue: "Permission denied" accessing chroma_db folder
**Symptoms:** Permission error when ChromaDB tries to read/write

**Solutions:**
```bash
# Fix permissions
chmod -R 755 chroma_db/
chmod -R u+rwx chroma_db/

# Or delete and recreate
rm -rf chroma_db/
python chroma_rag_system.py
```

#### Issue: "chroma_db is locked"
**Symptoms:** Database locked error when running multiple instances

**Solutions:**
```bash
# Make sure only ONE process is accessing ChromaDB
# Close all Python processes:

# Linux/Mac
pkill -f "python chroma_rag_system.py"
pkill -f "python rag_api_server.py"

# Windows
taskkill /F /IM python.exe

# Then retry
python chroma_rag_system.py
```

---

### ❌ Web Interface Issues

#### Issue: `rag_interface.html` shows blank page
**Symptoms:** HTML loads but no content visible

**Solutions:**
```bash
# 1. Check browser console for errors
# Right-click → Inspect → Console tab

# 2. Verify chunks_data.json exists
ls -la chunks_data.json

# 3. If not, regenerate it
python chroma_rag_system.py

# 4. Refresh browser
# Ctrl+Shift+R (hard refresh)
# Cmd+Shift+R (Mac)

# 5. Try different browser (Chrome/Firefox/Safari)
```

#### Issue: Query interface shows "Loading chunks..." forever
**Symptoms:** Chunks container shows infinite loading state

**Solutions:**
```bash
# 1. Wait 10 seconds (might be loading)

# 2. Open browser console (F12)
# Look for network errors or JavaScript errors

# 3. Verify chunks_data.json format
python -c "
import json
with open('chunks_data.json') as f:
    data = json.load(f)
    print(f'Total chunks: {len(data[\"chunks\"])}')
"

# 4. Manually trigger ingestion
python chroma_rag_system.py

# 5. Hard refresh browser (Ctrl+Shift+R)
```

#### Issue: "CORS error" when querying
**Symptoms:** Browser console shows CORS/cross-origin error

**Solutions:**
```bash
# Option 1: Use HTML without API server
# Just open rag_interface.html in browser (works offline)

# Option 2: Start API server (enables server calls)
python rag_api_server.py
# Then update HTML to point to server:
# const API_BASE = "http://localhost:8000"

# Option 3: Python http.server
cd Chapter_08_RAG
python -m http.server 8000
# Then visit: http://localhost:8000/rag_interface.html
```

---

### ❌ Groq API Issues

#### Issue: "Invalid API Key" error
**Symptoms:** Groq API rejects API key

**Solutions:**
```bash
# 1. Verify API key format
# Should start with: gsk_...
# Should be ~80+ characters

# 2. Check for copy errors
# Make sure there are no spaces or extra characters

# 3. Get new key from Groq
# Visit: https://console.groq.com
# Sign in → API Keys → Generate New Key

# 4. Test with curl
curl https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer gsk_YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mixtral-8x7b-32768",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

#### Issue: "API quota exceeded" or "Rate limit"
**Symptoms:** Groq API rejects requests with rate limit error

**Solutions:**
```bash
# 1. Wait before retrying (rate limit timeout)
time.sleep(60)

# 2. Use fewer top_k results (less processing)
# Edit rag_interface.html:
const topK = 3;  # Instead of 5

# 3. Check Groq console for usage
# Visit: https://console.groq.com/usage

# 4. Consider upgrading Groq account if on free tier
```

#### Issue: Network error / "Connection refused"
**Symptoms:** Cannot connect to Groq API

**Solutions:**
```bash
# 1. Check internet connection
ping api.groq.com

# 2. Check firewall
# Some firewalls block external API calls
# Try on different network or disable firewall

# 3. Check Groq service status
# Visit: https://status.groq.com

# 4. Try alternative LLM
# Switch to Claude, OpenAI, or local model
```

---

### ❌ Search & Query Issues

#### Issue: "No results found" for valid query
**Symptoms:** Query returns empty or irrelevant results

**Solutions:**
```bash
# 1. Verify PDFs were ingested
python -c "
from chroma_rag_system import ChromaRAGSystem
rag = ChromaRAGSystem()
stats = rag.get_collection_stats()
print(f'Total docs: {stats[\"total_documents\"]}')
"

# 2. Try exact phrase from PDF
# Make sure query matches PDF content

# 3. Increase top_k for more results
# Edit rag_interface.html:
const topK = 10;  # Try getting more results

# 4. Check chunk quality
# View chunks_data.json to see what was extracted
# If chunks are garbage, PDF might be corrupted
```

#### Issue: Irrelevant results / Low similarity scores
**Symptoms:** Retrieved chunks don't match query

**Solutions:**
```bash
# 1. Adjust chunking parameters
# Edit chroma_rag_system.py:
chunk_size = 2000      # Larger context
chunk_overlap = 500    # More overlap

# 2. Try synonyms in query
# Instead of "features", try "capabilities", "functions"

# 3. Verify embedding model is active
python -c "
from nomic import embed
result = embed.text(
    model='nomic-embed-text-v1.5',
    texts=['test']
)
print(result)
"

# 4. Re-ingest PDF with better settings
rm -rf chroma_db/
python chroma_rag_system.py
```

---

### ❌ Performance Issues

#### Issue: Slow query response (>10 seconds)
**Symptoms:** Queries take very long to complete

**Solutions:**
```bash
# 1. Reduce top_k results
# Instead of 10, use 3
const topK = 3;

# 2. Check network latency to Groq
# Groq API might be slow due to load

# 3. Monitor system resources
# python chroma_rag_system.py might be using too much memory

# 4. Reduce chunk size for faster embedding
chunk_size = 500  # Instead of 1000
```

#### Issue: ChromaDB search is slow
**Symptoms:** Search itself (before Groq) is slow

**Solutions:**
```bash
# ChromaDB should be <100ms, if slower:

# 1. Reduce number of documents
# Delete old documents from ChromaDB:
rm -rf chroma_db/

# 2. Check disk space
df -h          # Linux/Mac
dir C:         # Windows

# 3. Verify hardware specs
# ChromaDB on SSD is much faster than HDD
```

---

### ❌ Memory Issues

#### Issue: "MemoryError" or "Out of memory"
**Symptoms:** Python crashes with memory error

**Solutions:**
```bash
# 1. Process PDFs individually
# Instead of all at once:
python -c "
from chroma_rag_system import ChromaRAGSystem
rag = ChromaRAGSystem()
rag.ingest_pdf('./data/file1.pdf')
# Wait, then:
rag.ingest_pdf('./data/file2.pdf')
"

# 2. Reduce chunk size
chunk_size = 500  # Smaller = less memory

# 3. Close other applications
# Free up system memory

# 4. Upgrade system RAM or use cloud
# For large PDFs, consider cloud solutions
```

---

### ❌ API Server Issues

#### Issue: FastAPI server won't start
**Symptoms:** Error when running `python rag_api_server.py`

**Solutions:**
```bash
# 1. Check if port 8000 is in use
lsof -i :8000              # Linux/Mac
netstat -ano | findstr :8000  # Windows

# 2. Use different port
# Edit rag_api_server.py:
uvicorn.run(app, host="0.0.0.0", port=8001)

# 3. Check if uvicorn is installed
pip install uvicorn fastapi

# 4. Run without background processes
# Just: python rag_api_server.py
```

#### Issue: API endpoint returns 500 error
**Symptoms:** `/search` or `/ingest` returns Internal Server Error

**Solutions:**
```bash
# 1. Check server console for error details
# Look at terminal where rag_api_server.py is running

# 2. Test manually
python -c "
from chroma_rag_system import ChromaRAGSystem
rag = ChromaRAGSystem()
results = rag.search('test query')
print(results)
"

# 3. Check data folder
ls -la data/

# 4. Recreate ChromaDB
rm -rf chroma_db/
python setup.py
```

---

## 🆘 Advanced Debugging

### Enable verbose logging
```python
# Edit chroma_rag_system.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run with debug output
python chroma_rag_system.py
```

### Test each component separately
```bash
# Test PDF extraction
python -c "
from PyPDF2 import PdfReader
pdf = PdfReader('./data/your_pdf.pdf')
print(f'Pages: {len(pdf.pages)}')
print(pdf.pages[0].extract_text()[:200])
"

# Test embedding
python -c "
from nomic import embed
result = embed.text(model='nomic-embed-text-v1.5', texts=['hello world'])
print(f'Vector size: {len(result[\"embeddings\"][0])}')
"

# Test ChromaDB
python -c "
import chromadb
client = chromadb.Client()
collection = client.create_collection(name='test')
collection.add(ids=['1'], documents=['hello'])
results = collection.query(query_texts=['hello'], n_results=1)
print(results)
"

# Test Groq API
python -c "
from groq import Groq
client = Groq(api_key='gsk_YOUR_KEY_HERE')
msg = client.chat.completions.create(
    model='mixtral-8x7b-32768',
    messages=[{'role': 'user', 'content': 'Hello'}],
    max_tokens=100
)
print(msg.choices[0].message.content)
"
```

### Check file integrity
```bash
# Verify all files are in place
ls -la Chapter_08_RAG/
# Should have:
# - chroma_rag_system.py
# - rag_api_server.py
# - rag_interface.html
# - requirements_chroma_rag.txt
# - setup.py

# Check JSON validity
python -m json.tool chunks_data.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON"
```

---

## 📞 When Nothing Works

1. **Delete everything and restart**
   ```bash
   rm -rf chroma_db/
   rm -rf data/*.pdf
   python setup.py
   ```

2. **Check system requirements**
   - Python 3.8+
   - 2GB+ disk space
   - 4GB+ RAM
   - Internet connection

3. **Create fresh environment**
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # or: venv\Scripts\activate (Windows)
   pip install -r requirements_chroma_rag.txt
   python setup.py
   ```

4. **Check logs**
   - Browser console (F12)
   - Terminal output (run with -v flag)
   - chroma_db/ logs

5. **Seek help**
   - Check RAG_SETUP_GUIDE.md
   - Check QUICK_REFERENCE.md
   - Review file docstrings
   - Check ARCHITECTURE_DIAGRAMS.html

---

**Last updated:** May 2026
**System:** VWO RAG with ChromaDB + Nomic Embed + Groq
