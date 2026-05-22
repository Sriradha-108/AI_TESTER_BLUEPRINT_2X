@echo off
REM VWO RAG System - Quick Start Setup (Windows)

echo.
echo 🚀 VWO RAG System - Quick Start Setup
echo ======================================
echo.

REM Step 1: Check Python
echo ✓ Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+
    exit /b 1
)

REM Step 2: Create data folder
echo.
echo ✓ Creating ./data folder...
if not exist "data" mkdir data
echo   📂 ./data folder created

REM Step 3: Install dependencies
echo.
echo ✓ Installing dependencies...
pip install -r requirements_chroma_rag.txt

REM Step 4: Initialize ChromaDB
echo.
echo ✓ Initializing ChromaDB...
if not exist "chroma_db" mkdir chroma_db
echo   🗄️ ChromaDB directory created

REM Step 5: Instructions
echo.
echo ======================================
echo ✅ Setup Complete!
echo ======================================
echo.
echo 📋 Next Steps:
echo   1. Copy your VWO PDF to: ./data/vwo_requirements.pdf
echo   2. Run: python chroma_rag_system.py
echo   3. Open: rag_interface.html in your browser
echo   4. Add Groq API key and start querying!
echo.
echo 🔑 Groq API Key: gsk_YOUR_GROQ_API_KEY_HERE
echo.
echo 📚 For detailed instructions, see: RAG_SETUP_GUIDE.md
echo.
pause
