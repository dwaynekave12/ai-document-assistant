import sys

import numpy as np
from sentence_transformers import SentenceTransformer

from chunker import Chunk, chunk_pages
from extract import extract_pages

# Load the model once, when the file is imported (loading is slow, using it is fast)
model = SentenceTransformer("all-MiniLM-L6-v2")


class Retriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.embeddings = model.encode(
            [chunk.text for chunk in chunks],
            normalize_embeddings=True,
        )

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        """Return the top_k chunks most similar in meaning to the query."""
        query_embedding = model.encode(query, normalize_embeddings=True)
        scores = self.embeddings @ query_embedding
        best = np.argsort(scores)[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in best]


if __name__ == "__main__":
    pdf_path, query = sys.argv[1], sys.argv[2]
    chunks = chunk_pages(extract_pages(pdf_path))
    retriever = Retriever(chunks)

    for chunk, score in retriever.search(query):
        print(f"[Page {chunk.page}] score={score:.3f}  {chunk.text[:120]}...\n")