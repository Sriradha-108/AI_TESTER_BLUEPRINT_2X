#!/usr/bin/env python3
"""
VWO RAG System - Automated Setup Script
This script handles the complete setup of the RAG system
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)

def print_step(text):
    """Print a step with checkmark"""
    print(f"\n✓ {text}")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def run_command(command):
    """Run a shell command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print_error(f"Command failed: {command}")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print_error(f"Failed to run command: {e}")
        return False

def setup_rag_system():
    """Main setup function"""
    print_header("🚀 VWO RAG System - Automated Setup")
    
    # Step 1: Check Python version
    print_step(f"Checking Python installation...")
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info < (3, 8):
        print_error(f"Python 3.8+ required, but found {version}")
        return False
    print_success(f"Python {version} found")
    
    # Step 2: Check current directory
    current_dir = Path.cwd()
    print_step(f"Setting up in: {current_dir}")
    
    # Step 3: Create data folder
    print_step("Creating ./data folder...")
    data_dir = current_dir / "data"
    data_dir.mkdir(exist_ok=True)
    print_success(f"Created {data_dir}")
    
    # Step 4: Create chroma_db folder
    print_step("Creating ./chroma_db folder...")
    chroma_dir = current_dir / "chroma_db"
    chroma_dir.mkdir(exist_ok=True)
    print_success(f"Created {chroma_dir}")
    
    # Step 5: Check for requirements file
    print_step("Checking requirements file...")
    req_file = current_dir / "requirements_chroma_rag.txt"
    if not req_file.exists():
        print_error(f"requirements_chroma_rag.txt not found in {current_dir}")
        return False
    print_success(f"Found requirements file")
    
    # Step 6: Install dependencies
    print_step("Installing Python dependencies...")
    print_info("This may take a few minutes...")
    
    pip_command = f"{sys.executable} -m pip install -r requirements_chroma_rag.txt"
    if not run_command(pip_command):
        print_error("Failed to install dependencies")
        return False
    print_success("Dependencies installed")
    
    # Step 7: Verify ChromaDB installation
    print_step("Verifying ChromaDB installation...")
    try:
        import chromadb
        print_success(f"ChromaDB {chromadb.__version__} installed")
    except ImportError:
        print_error("ChromaDB not found after installation")
        return False
    
    # Step 8: Test RAG system initialization
    print_step("Testing RAG system initialization...")
    try:
        from chroma_rag_system import ChromaRAGSystem
        rag = ChromaRAGSystem()
        print_success("RAG system initialized successfully")
    except Exception as e:
        print_error(f"Failed to initialize RAG system: {e}")
        return False
    
    return True

def print_next_steps():
    """Print next steps for the user"""
    print_header("✅ Setup Complete!")
    
    print("""
📋 NEXT STEPS:

  1️⃣  Add your VWO PDF:
      Copy your VWO product requirements PDF to:
      → ./data/vwo_requirements.pdf

  2️⃣  Ingest the PDF:
      Run: python chroma_rag_system.py
      This will extract text, create chunks, and store in ChromaDB

  3️⃣  View the interface:
      Open: rag_interface.html in your web browser
      Or start the API server: python rag_api_server.py

  4️⃣  Query with Groq:
      a) Get API key from: https://console.groq.com
      b) Paste key in the HTML interface
      c) Ask questions about VWO!

📚 DOCUMENTATION:
   → See RAG_SETUP_GUIDE.md for detailed instructions
   → See individual file docstrings for implementation details

🔑 YOUR GROQ API KEY:
   gsk_YOUR_GROQ_API_KEY_HERE

🗂️  FILE STRUCTURE CREATED:
   ├── data/                         ← Add PDFs here
   ├── chroma_db/                    ← ChromaDB storage
   ├── chroma_rag_system.py          ← RAG engine
   ├── rag_api_server.py             ← API server
   ├── rag_interface.html            ← Web interface
   ├── chunks_data.json              ← (Generated after ingestion)
   └── RAG_SETUP_GUIDE.md            ← Full documentation

❓ TROUBLESHOOTING:
   • "ModuleNotFoundError: No module named 'chromadb'"
     → pip install chromadb
   
   • "No PDFs found in data folder"
     → Copy your PDF to ./data/ first
   
   • "Groq API Error"
     → Check your API key at https://console.groq.com

📧 For help: Check RAG_SETUP_GUIDE.md or the file docstrings
    """)

def main():
    """Main entry point"""
    try:
        # Run setup
        if not setup_rag_system():
            print_error("Setup failed!")
            sys.exit(1)
        
        # Print next steps
        print_next_steps()
        
        print_success("Ready to use!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
