"""Parse a PDF, chunk the text, embed chunks, and store them in ChromaDB."""

import os
import shutil
import sys

import chromadb
import pypdf
import pypdf.errors
from dotenv import load_dotenv
from voyageai.client import Client as VoyageClient

from consts import CHROMA_COLLECTION_NAME, CHROMA_STORE_DIR, EMBEDDING_MODEL

# Characters per chunk; last chunk may be shorter.
CHUNK_SIZE = 1000
# Characters of overlap between consecutive chunks.
CHUNK_OVERLAP = 200


def parse_pdf(path: str) -> tuple[list[str], int]:
    """Open a PDF and return per-page text strings plus the page count."""
    reader = pypdf.PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    page_count = len(pages)
    if not "".join(pages).strip():
        raise ValueError("PDF contains no extractable text.")
    return pages, page_count


def chunk_text(pages: list[str]) -> list[dict[str, int | str]]:
    """Split per-page texts into overlapping fixed-size chunks.

    Chunking happens per page so page_number metadata is exact.
    """
    chunks: list[dict[str, int | str]] = []
    chunk_index = 0
    for page_number, text in enumerate(pages, start=1):
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            fragment = text[start:end]
            if fragment.strip():
                chunks.append(
                    {
                        "text": fragment,
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                    }
                )
                chunk_index += 1
            start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def build_chroma_collection(store_dir: str) -> chromadb.Collection:
    """Remove any existing store, create a fresh PersistentClient, return the collection."""
    if os.path.exists(store_dir):
        shutil.rmtree(store_dir)
    client = chromadb.PersistentClient(path=store_dir)
    return client.get_or_create_collection(CHROMA_COLLECTION_NAME)


def embed_chunk(vo: VoyageClient, text: str) -> list[float] | list[int]:
    """Call Voyage AI for a single chunk, return the embedding vector."""
    result = vo.embed([text], model=EMBEDDING_MODEL, input_type="document")
    return result.embeddings[0]


def store_chunks(
    collection: chromadb.Collection,
    chunks: list[dict[str, int | str]],
    embeddings: list[list[float] | list[int]],
) -> None:
    """Batch-insert chunks and their embeddings into ChromaDB."""
    collection.add(
        ids=[f"chunk_{chunk['chunk_index']}" for chunk in chunks],
        embeddings=embeddings,  # type: ignore[arg-type]
        documents=[str(chunk["text"]) for chunk in chunks],
        metadatas=[
            {
                "page_number": int(chunk["page_number"]),
                "chunk_index": int(chunk["chunk_index"]),
            }
            for chunk in chunks
        ],
    )


def main() -> None:
    """CLI entry point: parse PDF, embed chunks, store in Chroma."""
    load_dotenv()

    if len(sys.argv) != 2:
        print("Usage: python ingest.py <path-to-pdf>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    voyage_api_key = os.environ.get("VOYAGE_API_KEY")
    if not voyage_api_key:
        print(
            "Error: VOYAGE_API_KEY is not set — check your .env file",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        pages, page_count = parse_pdf(path)
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except pypdf.errors.FileNotDecryptedError:
        print(
            f"Error: PDF is encrypted and cannot be read: {path}",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    chunks = chunk_text(pages)
    total = len(chunks)

    vo = VoyageClient(api_key=voyage_api_key)
    collection = build_chroma_collection(CHROMA_STORE_DIR)

    embeddings: list[list[float] | list[int]] = []
    for i, chunk in enumerate(chunks, start=1):
        print(f"Embedding chunk {i}/{total}...")
        try:
            vector = embed_chunk(vo, str(chunk["text"]))
        except Exception as exc:
            print(f"Error embedding chunk {i}/{total}: {exc}", file=sys.stderr)
            sys.exit(1)
        embeddings.append(vector)

    store_chunks(collection, chunks, embeddings)
    print(
        f"Done. Stored {total} chunks from {page_count} pages into {CHROMA_STORE_DIR}"
    )


if __name__ == "__main__":
    main()
