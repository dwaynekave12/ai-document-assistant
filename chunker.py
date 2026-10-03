import sys
from dataclasses import dataclass

from extract import extract_pages


@dataclass
class Chunk:
    text: str
    page: int


def chunk_pages(pages: list[str], chunk_size: int = 200, overlap: int = 40) -> list[Chunk]:
    """Split each page into overlapping chunks of roughly chunk_size words."""
    chunks = []
    step = chunk_size - overlap

    for page_number, page_text in enumerate(pages, start=1):
        words = page_text.split()
        if not words:
            continue  # skip empty pages

        for start in range(0, len(words), step):
            piece = words[start:start + chunk_size]
            chunks.append(Chunk(text=" ".join(piece), page=page_number))
            if start + chunk_size >= len(words):
                break  # this piece reached the end of the page

    return chunks


if __name__ == "__main__":
    pages = extract_pages(sys.argv[1])
    chunks = chunk_pages(pages)

    print(f"{len(pages)} pages -> {len(chunks)} chunks\n")
    for chunk in chunks[:3]:
        print(f"[Page {chunk.page}] {chunk.text[:150]}...\n")