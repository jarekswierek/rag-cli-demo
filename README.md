# rag-cli-demo

> **Work in progress.** `ingest.py` (PDF parsing, chunking, embedding, and storage in ChromaDB) is completed. `ask.py` (query pipeline with citations) is not yet implemented.

An educational example of a Retrieval-Augmented Generation (RAG) pipeline in the terminal.

## What is this?

RAG is a pattern where a language model answers questions using text retrieved from your own documents, rather than relying solely on its training data. This project ingests a PDF, splits it into chunks, embeds them with Voyage AI, stores them in ChromaDB, and lets you ask questions answered by Claude — with page-number citations.

## Prerequisites

- Python 3.14+
- [Poetry](https://python-poetry.org/docs/#installation)
- Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com)
- Voyage AI API key — get one at [dash.voyageai.com](https://dash.voyageai.com)

## Installation

```bash
git clone https://github.com/jarekswierek/rag-cli-demo.git
cd rag-cli-demo
cp .env.example .env
# open .env and set ANTHROPIC_API_KEY and VOYAGE_API_KEY
make install
```

## Usage

**Ingest a PDF:**

```bash
make ingest PDF=docs/sample.pdf
```

**Ask a question:**

```bash
make ask PDF=docs/sample.pdf Q="What are the main conclusions?"
```

> `ask.py` is not implemented yet — this command doesn't work yet.

## Example output

```text
Embedding chunk 1/23...
Embedding chunk 2/23...
...
Done. Stored 23 chunks from 8 pages into ./chroma_store/
```

## How it works

```
PDF file
   │
   ▼
pypdf — extract text page by page
   │
   ▼
Fixed-size chunking (1000 chars, 200 overlap) with page metadata
   │
   ▼
Anthropic voyage-3 — embed each chunk
   │
   ▼
ChromaDB — store vectors + metadata locally (./chroma_store/)
   │
   ▼
Question → voyage-3 embedding → ChromaDB similarity search (top 3)
   │
   ▼
Claude claude-haiku-4-5 — answer with citations
   │
   ▼
Terminal output: cited chunks + answer
```
