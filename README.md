# rag-cli-demo

> **Work in progress.** `ingest.py` (PDF parsing, chunking, embedding, and storage in ChromaDB) is in progress. `ask.py` (query pipeline with citations) is not yet implemented.

An educational example of a Retrieval-Augmented Generation (RAG) pipeline in the terminal.

## What is this?

RAG is a pattern where a language model answers questions using text retrieved from your own documents, rather than relying solely on its training data. This project ingests a PDF, splits it into chunks, embeds them with Voyage AI, stores them in ChromaDB, and lets you ask questions answered by Claude — with page-number citations.

## Prerequisites

- Python 3.14+
- [Poetry](https://python-poetry.org/docs/#installation)
- Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com)

## Installation

```bash
git clone https://github.com/jarekswierek/rag-cli-demo.git
cd rag-cli-demo
cp .env.example .env
# open .env and set ANTHROPIC_API_KEY=your-actual-key
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

## Example output

```text
Embedding chunk 1/23...
Embedding chunk 2/23...
...
Done. Stored 23 chunks from 8 pages into ./chroma_store/
```

```text
Context used to answer:
[1] Page 3: "The study found that retrieval-augmented models outperform
    fine-tuned baselines on open-domain QA tasks by a margin of 12%..."
[2] Page 5: "Key limitations include latency introduced by the retrieval
    step and sensitivity to chunk size during indexing..."
[3] Page 7: "Authors recommend a chunk size of 512–1024 tokens with a
    20% overlap to balance context coherence and retrieval precision..."
---
Answer:
The main conclusions are that RAG models significantly outperform fine-tuned
baselines on open-domain QA, though practitioners must account for retrieval
latency and tune chunk size carefully — the authors recommend 512–1024 tokens
with ~20% overlap.
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
