import os
import uuid

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

from chunker import Chunk
from retriever import EMBEDDING_DIMENSIONS, embed_query, embed_texts

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]


def init_db() -> None:
    """Create the pgvector extension and tables if they don't exist yet."""
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY,
                filename TEXT NOT NULL,
                page_count INTEGER NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                page INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding vector({EMBEDDING_DIMENSIONS}) NOT NULL
            )
        """)


def get_connection() -> psycopg.Connection:
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)  # lets us pass numpy arrays straight into vector columns
    return conn


def save_document(filename: str, page_count: int, chunks: list[Chunk]) -> uuid.UUID:
    """Embed the chunks and save the document and its chunks in one transaction."""
    embeddings = embed_texts([chunk.text for chunk in chunks])
    document_id = uuid.uuid4()

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO documents (id, filename, page_count) VALUES (%s, %s, %s)",
            (document_id, filename, page_count),
        )
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO chunks (document_id, page, text, embedding) VALUES (%s, %s, %s, %s)",
                [
                    (document_id, chunk.page, chunk.text, embedding)
                    for chunk, embedding in zip(chunks, embeddings)
                ],
            )

    return document_id


def document_exists(document_id: uuid.UUID) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM documents WHERE id = %s", (document_id,)
        ).fetchone()
    return row is not None


class DatabaseRetriever:
    """Same search() interface as Retriever, but the search runs inside PostgreSQL."""

    def __init__(self, document_id: uuid.UUID):
        self.document_id = document_id

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        query_embedding = embed_query(query)
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT page, text, 1 - (embedding <=> %s) AS score
                FROM chunks
                WHERE document_id = %s
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (query_embedding, self.document_id, query_embedding, top_k),
            ).fetchall()

        return [(Chunk(text=text, page=page), float(score)) for page, text, score in rows]