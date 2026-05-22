#!/bin/bash

# VWO RAG System - Quick Start Script
# This script automates the setup process

echo "🚀 VWO RAG System - Quick Start Setup"
echo "======================================"
echo ""

# Step 1: Check Python
echo "✓ Checking Python installation..."
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+"
    exit 1
fi
python --version

# Step 2: Create data folder
echo ""
echo "✓ Creating ./data folder..."
mkdir -p ./data
echo "  📂 ./data folder created"

# Step 3: Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install -r requirements_chroma_rag.txt

# Step 4: Initialize ChromaDB
echo ""
echo "✓ Initializing ChromaDB..."
mkdir -p ./chroma_db
echo "  🗄️ ChromaDB directory created"

# Step 5: Instructions
echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "📋 Next Steps:"
echo "  1. Copy your VWO PDF to: ./data/vwo_requirements.pdf"
echo "  2. Run: python chroma_rag_system.py"
echo "  3. Open: rag_interface.html in your browser"
echo "  4. Add Groq API key and start querying!"
echo ""
echo "🔑 Groq API Key: gsk_YOUR_GROQ_API_KEY_HERE"
echo ""
echo "📚 For detailed instructions, see: RAG_SETUP_GUIDE.md"
echo ""
