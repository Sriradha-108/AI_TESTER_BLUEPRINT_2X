"""
RAG System using ChromaDB and Nomic Embed
Ingests PDFs and provides semantic search + LLM generation with Groq
"""

import os
import json
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from PyPDF2 import PdfReader
import hashlib
from datetime import datetime

class ChromaRAGSystem:
    def __init__(self, persist_dir="./chroma_db", data_dir="./data"):
        """Initialize ChromaDB with persistent storage"""
        self.persist_dir = persist_dir
        self.data_dir = data_dir
        self.chunks_metadata = []
        
        # Create directories if they don't exist
        os.makedirs(persist_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize ChromaDB client with new API (persistent)
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="vwo_app_docs",
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"✅ ChromaDB initialized at: {persist_dir}")
        print(f"✅ Collection: {self.collection.name}")
        print(f"📊 Current docs in collection: {self.collection.count()}")

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            text = ""
            pdf_reader = PdfReader(pdf_path)
            total_pages = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                text += f"\n\n--- Page {page_num} ---\n{page_text}"
            
            print(f"📄 Extracted {total_pages} pages from {Path(pdf_path).name}")
            return text
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            return None

    def chunk_text(self, text, chunk_size=1000, chunk_overlap=200):
        """Split text into chunks using RecursiveCharacterTextSplitter"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        chunks = splitter.split_text(text)
        print(f"✂️  Split into {len(chunks)} chunks")
        return chunks

    def ingest_pdf(self, pdf_path, source_name=None):
        """Ingest a PDF into ChromaDB"""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            print(f"❌ PDF not found: {pdf_path}")
            return
        
        source_name = source_name or pdf_path.name
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return
        
        # Chunk the text
        chunks = self.chunk_text(text)
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{source_name.replace('.pdf', '')}_chunk_{i}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "source": source_name,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "ingested_at": datetime.now().isoformat(),
            })
            
            # Store for visualization
            self.chunks_metadata.append({
                "id": chunk_id,
                "source": source_name,
                "chunk_index": i,
                "content": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                "length": len(chunk),
            })
        
        # Add to ChromaDB (embeddings are generated automatically with nomic-embed-text)
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        
        print(f"✅ Ingested {len(chunks)} chunks from {source_name}")
        return len(chunks)

    def search(self, query, top_k=5):
        """Search for relevant chunks"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
            )
            
            # Format results
            search_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results['distances'] else 0
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    search_results.append({
                        "rank": i + 1,
                        "content": doc,
                        "source": metadata.get('source', 'Unknown'),
                        "chunk_index": metadata.get('chunk_index', 0),
                        "distance": float(distance),
                        "similarity": 1 - float(distance),  # Convert distance to similarity
                    })
            
            return search_results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def get_collection_stats(self):
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection.name,
            "embeddings_model": "nomic-embed-text (Nomic AI)",
        }

    def export_chunks_for_visualization(self, output_file="chunks_data.json"):
        """Export chunks metadata for HTML visualization"""
        data = {
            "metadata": self.get_collection_stats(),
            "chunks": self.chunks_metadata,
            "export_time": datetime.now().isoformat(),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported chunks data to {output_file}")
        return data

    def list_files_in_data_folder(self):
        """List all PDF files in the data folder"""
        pdf_files = list(Path(self.data_dir).glob("*.pdf"))
        return [str(f) for f in pdf_files]

# Main execution
if __name__ == "__main__":
    # Initialize RAG system
    rag = ChromaRAGSystem(persist_dir="./chroma_db", data_dir="./data")
    
    # Check for PDFs in data folder
    pdf_files = rag.list_files_in_data_folder()
    
    if pdf_files:
        print(f"\n📂 Found {len(pdf_files)} PDF file(s) in data folder")
        for pdf_file in pdf_files:
            print(f"  → {Path(pdf_file).name}")
            rag.ingest_pdf(pdf_file)
    else:
        print("\n⚠️  No PDF files found in ./data folder")
        print("📋 Please add PDF files to ingest them into ChromaDB")
        print("   Copy your VWO product requirements PDF to ./data/")
    
    # Export chunks for visualization
    rag.export_chunks_for_visualization("chunks_data.json")
    
    # Show stats
    stats = rag.get_collection_stats()
    print(f"\n📊 Collection Statistics:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Embeddings model: {stats['embeddings_model']}")
    
    # Example search (if documents exist)
    if stats['total_documents'] > 0:
        print("\n🔍 Example Search Query:")
        test_query = "What are the main features?"
        results = rag.search(test_query, top_k=3)
        print(f"   Query: '{test_query}'")
        print(f"   Found {len(results)} relevant chunks")
        for result in results:
            print(f"     [{result['rank']}] Similarity: {result['similarity']:.2%}")
