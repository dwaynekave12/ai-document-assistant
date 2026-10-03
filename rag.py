import sys

from ask import ask
from chunker import Chunk, chunk_pages
from extract import extract_pages
from retriever import Retriever


def build_context(results: list[tuple[Chunk, float]]) -> str:
    """Turn search results into page-labelled text, in page order."""
    ordered = sorted(results, key=lambda result: result[0].page)
    return "\n\n".join(f"--- Page {chunk.page} ---\n{chunk.text}" for chunk, _ in ordered)


def answer_question(retriever: Retriever, question: str, top_k: int = 5):
    """Retrieve the most relevant chunks, then ask Claude using only those."""
    results = retriever.search(question, top_k=top_k)
    context = build_context(results)
    answer = ask(context, question)
    return answer, results


if __name__ == "__main__":
    pdf_path, question = sys.argv[1], sys.argv[2]
    retriever = Retriever(chunk_pages(extract_pages(pdf_path)))

    answer, results = answer_question(retriever, question)
    print(answer)

    pages = sorted({chunk.page for chunk, _ in results})
    print(f"\nPages sent to Claude: {pages}")