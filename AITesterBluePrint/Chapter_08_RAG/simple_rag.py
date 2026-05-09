import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Initialize Rich Console for beautiful printing
console = Console()

def simple_rag_demo():
    # 1. Load the document
    file_path = "story_of_tta.txt"
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/] {file_path} not found!")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    console.print(Panel.fit("Starting Simple RAG Demo: Chunking & Embedding", style="bold magenta"))

    # 2. Chunking the document
    # We use RecursiveCharacterTextSplitter which tries to keep paragraphs, then sentences together.
    # Chunk size: 500 characters, Overlap: 50 characters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = text_splitter.create_documents([text])
    
    # 3. Print the chunks
    table = Table(title="Document Chunks Visualization")
    table.add_column("Chunk #", justify="center", style="cyan", no_wrap=True)
    table.add_column("Content Preview", style="green")
    table.add_column("Length", justify="right", style="dim")

    chunk_data_for_export = []
    
    for i, chunk in enumerate(chunks):
        content = chunk.page_content.replace("\n", " ")
        preview = content[:100] + "..." if len(content) > 100 else content
        table.add_row(str(i+1), preview, str(len(chunk.page_content)))
        
        chunk_data_for_export.append({
            "id": i + 1,
            "content": chunk.page_content,
            "length": len(chunk.page_content)
        })

    console.print(table)
    console.print(f"\n[bold green]Total Chunks Created:[/] {len(chunks)}")

    # 4. Show how "Nomic Embed" would be used
    # Note: This requires Ollama running locally with `ollama pull nomic-embed-text`
    console.print("\n[bold yellow]Embedding Step (Simulated/Actual):[/]")
    console.print("Using Model: [bold cyan]nomic-embed-text[/]")
    
    try:
        import ollama
        # We'll just show the logic for the first chunk to avoid long waits
        console.print("[dim]Attempting to get embedding for Chunk #1 using Ollama...[/]")
        # response = ollama.embeddings(model="nomic-embed-text", prompt=chunks[0].page_content)
        # console.print(f"[green]Successfully generated embedding! Vector size: {len(response['embedding'])}[/]")
        console.print("[green]Code logic: ollama.embeddings(model='nomic-embed-text', prompt=chunk_content)[/]")
    except Exception as e:
        console.print(f"[dim red]Ollama embedding call skipped (ensure Ollama is running and model is pulled). Error: {e}[/]")

    # 5. Export to JS for HTML visualization (Avoids CORS issues)
    export_path = "rag_data.js"
    with open(export_path, "w", encoding="utf-8") as f:
        f.write("const ragData = ")
        json.dump(chunk_data_for_export, f, indent=4)
        f.write(";")
    
    console.print(f"\n[bold green]Data exported to {export_path} for HTML visualization![/]")

if __name__ == "__main__":
    simple_rag_demo()
