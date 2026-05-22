# AI Tester Blueprint 2.0

Welcome to the **AI Tester Blueprint** repository. This project is a comprehensive guide and toolkit for modern software testers who want to leverage AI, LLMs, and RAG (Retrieval-Augmented Generation) in their testing workflows.

## 📁 Project Structure

This repository is organized into chapters, projects, and lectures, each focusing on a specific aspect of AI-driven testing:

### 📖 Chapters
- **Chapter_03_Job_Assistance_AI**: AI tools for career growth and job applications.
- **Chapter_04_AI_Agents**: Building and deploying autonomous agents for testing.
- **Chapter_07_AI_Agent_VIBE_Coding**: Advanced coding techniques for AI agents.
- **Chapter_08_RAG**: Retrieval-Augmented Generation for testing. Includes:
  - `simple_rag.py`: Python script for basic document chunking and embedding logic.
  - `chroma_rag_system.py`: Fully featured local RAG implementation using ChromaDB and Groq/Nomic embeddings.
  - `rag_api_server.py`: FastAPI server exposing RAG endpoints.
  - `rag_interface.html`: Beautiful, interactive web interface.
  - Detailed markdown guides (`RAG_SETUP_GUIDE.md`, `TROUBLESHOOTING.md`, etc.).
- **chapter_09_Project_QACopilot**: 🤖 **QA Copilot** — a multi-source RAG application for QA engineers working on app.vwo.com. Indexes Selenium Java code, Playwright TypeScript code, manual test cases (CSV), product PRDs (PDF), and JIRA bug exports (Markdown) into Qdrant, then routes natural-language queries via Groq `gpt-oss-120b` to return cited answers, generate new test cases from JIRA tickets, find similar test cases, or generate Selenium/Playwright automation code. Includes FastAPI backend, React + Vite + Tailwind frontend, an APScheduler-based hourly auto-ingest, and an `index.html` entry stub. See [chapter_09_Project_QACopilot/README.md](./chapter_09_Project_QACopilot/README.md).
- **chapter_10_MCP_Basics**: 🔌 **MCP Basics** — hands-on notes for wiring Model Context Protocol (MCP) servers into your editor. Includes [`Playwright_MCP/Nodes.md`](./chapter_10_MCP_Basics/Playwright_MCP/Nodes.md), a step-by-step guide for adding the official `@playwright/mcp` server to VS Code (Copilot Chat Agent mode) with both Command Palette and `mcp.json` configurations, common flags, troubleshooting tips, and a sample failure-case screenshot (`login_failed.png`) captured against `app.vwo.com` via Playwright MCP.

### 🎓 Lectures
- **Lecture_Playwright_CLI**: Quick reference and tutorials on utilizing Playwright's command line interface.
- **Lecture_playwright_AI_Agents**: Integration of Playwright automation within agentic AI workflows.

### 🛠️ Projects
- **Project_01_LocalTestGenerator_Antigravity**: Tooling for generating automated test cases locally using LLMs.
- **Project_02_RICE_POT_Selenium**: Integration guides and setup for running AI-driven Selenium test suites.
- **Project_02_Real_PE**: Real-world project configuration scripts.
- **Project_Test_Case_Generator**: Full-stack application (FastAPI + React) that integrates with Jira APIs to fetch user stories and generate editable, exportable test cases using Claude LLM. See [Project_Test_Case_Generator/README.md](./Project_Test_Case_Generator/README.md).

---

## 🚀 Getting Started with RAG Demo (Chapter 8)

The local RAG system in `Chapter_08_RAG` shows how to ingest a PDF document, chunk/embed it using ChromaDB, and query it via a local API server or custom web page.

### 1. Run the Ingestion
```powershell
cd Chapter_08_RAG
python chroma_rag_system.py
```

### 2. Launch the Web Interface
Double-click and open `rag_interface.html` directly in your browser. Provide your Groq API key to start querying your ingested documents!

---

## 🤖 Getting Started with QA Copilot (Chapter 9)

A powerful retrieval-augmented agent to query test case repositories, manuals, Jira tickets, and generate automated test code.

### 1. Installation & Ingestion
```powershell
cd chapter_09_Project_QACopilot
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt

# Run the ingestion script (embeds Selenium/Playwright code, Jira docs, PRDs, etc.)
python -m backend.ingest.ingest_all
```

### 2. Run the App
```powershell
# Start FastAPI backend (Port 8000)
uvicorn backend.main:app --port 8000

# Start React Frontend (in a new terminal window)
cd frontend
npm install
npm run dev
```

---

## 📋 Getting Started with Jira Test Case Generator (Project)

Generate structured test cases automatically from Jira tickets.

### 1. Startup Services
```powershell
cd Project_Test_Case_Generator

# Start backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.main

# Start frontend (in a separate terminal)
cd ../frontend
npm install
npm run dev
```

---

## 🤝 Community
Join the movement at **The Testing Academy** and let's revolutionize the way we test software!

---
*Created by Promod Dutta & The Testing Academy Community*
