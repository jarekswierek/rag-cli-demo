"""Parse a PDF, chunk the text, embed chunks, and store them in ChromaDB."""

import sys

import pypdf
import pypdf.errors

# Characters per chunk; last chunk may be shorter.
CHUNK_SIZE = 1000
# Characters of overlap between consecutive chunks.
CHUNK_OVERLAP = 200


def parse_pdf(path: str) -> tuple[list[str], int]:
    """Open a PDF and return per-page text strings plus the page count."""
    reader = pypdf.PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    page_count = len(pages)
    total_text = "".join(pages)
    if not total_text.strip():
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
            chunk_text_value = text[start:end]
            if chunk_text_value.strip():
                chunks.append(
                    {
                        "text": chunk_text_value,
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                    }
                )
                chunk_index += 1
            start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def main() -> None:
    """CLI entry point: parse PDF path from argv, chunk, print summary."""
    if len(sys.argv) != 2:
        print("Usage: python ingest.py <path-to-pdf>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

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
    print(f"Pages: {page_count} | Chunks: {len(chunks)}")


if __name__ == "__main__":
    main()
