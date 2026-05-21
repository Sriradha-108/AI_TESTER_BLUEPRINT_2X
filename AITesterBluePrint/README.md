# AI Tester Blueprint 2.0

Welcome to the **AI Tester Blueprint** repository. This project is a comprehensive guide and toolkit for modern software testers who want to leverage AI, LLMs, and RAG (Retrieval-Augmented Generation) in their testing workflows.

## 📁 Project Structure

This repository is organized into chapters and projects, each focusing on a specific aspect of AI-driven testing:

- **Chapter_03_Job_Assistance_AI**: AI tools for career growth and job applications.
- **Chapter_04_AI_Agents**: Building and deploying autonomous agents for testing.
- **Chapter_07_AI_Agent_VIBE_Coding**: Advanced coding techniques for AI agents.
- **Chapter_08_RAG**: Retrieval-Augmented Generation for testing.
  - `story_of_tta.txt`: A sample knowledge base document.
  - `simple_rag.py`: Python script for document chunking and embedding logic.
  - `index.html`: Interactive RAG Explorer visualization.
  - `chunks_report.html`: Detailed chunk analysis and audit report.
- **chapter_09_Project_QACopilot**: 🤖 **QA Copilot** — a multi-source RAG application for QA engineers working on app.vwo.com. Indexes Selenium Java code, Playwright TypeScript code, manual test cases (CSV), product PRDs (PDF), and JIRA bug exports (Markdown) into Qdrant, then routes natural-language queries via Groq `gpt-oss-120b` to return cited answers, generate new test cases from JIRA tickets, find similar test cases, or generate Selenium/Playwright automation code. Includes FastAPI backend, React + Vite + Tailwind frontend, and an APScheduler-based hourly auto-ingest. See [chapter_09_Project_QACopilot/README.md](./chapter_09_Project_QACopilot/README.md).
- **Project_01_LocalTestGenerator**: Generating test cases locally using LLMs.
- **Project_02_RICE_POT_Selenium**: Integrating AI with Selenium frameworks.

## 🚀 Getting Started with RAG Demo

The RAG demo in `Chapter_08_RAG` shows how to turn a document into searchable "chunks" that an AI can use to answer questions accurately.

### 1. Prerequisites
- Python 3.10+
- Installed libraries: `langchain`, `ollama`, `rich`
- [Ollama](https://ollama.com/) running locally (optional, for embeddings).

### 2. Run the Chunking Script
```powershell
cd Chapter_08_RAG
python simple_rag.py
```

### 3. View the Visualization
Open `index.html` or `chunks_report.html` in your browser to see the beautiful visualization of the processed data.

## 🤝 Community
Join the movement at **The Testing Academy** and let's revolutionize the way we test software!

---
*Created by Promod Dutta & The Testing Academy Community*
