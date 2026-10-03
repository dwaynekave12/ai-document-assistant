import sys

import numpy as np
from sentence_transformers import SentenceTransformer

from chunker import Chunk, chunk_pages
from extract import extract_pages

# Load the model once, when the file is imported (loading is slow, using it is fast)
model = SentenceTransformer("all-MiniLM-L6-v2")
EMBEDDING_DIMENSIONS = 384


def embed_texts(texts: list[str]) -> np.ndarray:
    """Turn a list of texts into normalised embeddings (one row per text)."""
    return model.encode(texts, normalize_embeddings=True)


def embed_query(query: str) -> np.ndarray:
    """Turn a single question into a normalised embedding."""
    return model.encode(query, normalize_embeddings=True)


class Retriever:
    """In-memory search, used by the command-line scripts."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.embeddings = embed_texts([chunk.text for chunk in chunks])

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        scores = self.embeddings @ embed_query(query)
        best = np.argsort(scores)[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in best]


if __name__ == "__main__":
    pdf_path, query = sys.argv[1], sys.argv[2]
    retriever = Retriever(chunk_pages(extract_pages(pdf_path)))

    for chunk, score in retriever.search(query):
        print(f"[Page {chunk.page}] score={score:.3f}  {chunk.text[:120]}...\n")