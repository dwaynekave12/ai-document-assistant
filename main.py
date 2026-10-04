import uuid
from contextlib import asynccontextmanager
from io import BytesIO
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from chunker import chunk_pages
from db import (
    DatabaseRetriever,
    delete_document,
    document_exists,
    init_db,
    list_documents,
    save_document,
)

from extract import extract_pages
from rag import answer_question

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # make sure the tables exist when the server starts
    yield


app = FastAPI(title="AI Document Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    pages: int
    chunks: int

class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    pages: int
    created_at: datetime

class QuestionRequest(BaseModel):
    question: str


class Source(BaseModel):
    page: int
    score: float


class AnswerResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents", response_model=UploadResponse)
def upload_document(file: UploadFile = File(...)):
    """Upload a PDF. It's chunked, embedded and saved to the database."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large (max 10 MB).")

    pages = extract_pages(BytesIO(contents))
    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(
            status_code=422,
            detail="No text found in this PDF. It may be a scanned image.",
        )

    document_id = save_document(file.filename, len(pages), chunks)

    return UploadResponse(
        document_id=str(document_id),
        filename=file.filename,
        pages=len(pages),
        chunks=len(chunks),
    )


@app.post("/documents/{document_id}/ask", response_model=AnswerResponse)
def ask_question(document_id: uuid.UUID, request: QuestionRequest):
    """Ask a question about a previously uploaded document."""
    if not document_exists(document_id):
        raise HTTPException(status_code=404, detail="Document not found.")

    retriever = DatabaseRetriever(document_id)
    answer, results = answer_question(retriever, request.question)
    sources = [Source(page=chunk.page, score=round(score, 3)) for chunk, score in results]

    return AnswerResponse(answer=answer, sources=sources)

@app.get("/documents", response_model=list[DocumentSummary])
def get_documents():
    """List all uploaded documents, newest first."""
    return list_documents()


@app.delete("/documents/{document_id}", status_code=204)
def remove_document(document_id: uuid.UUID):
    """Delete a document and all its chunks."""
    if not delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found.")