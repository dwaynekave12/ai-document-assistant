from io import BytesIO

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from ask import ask
from extract import extract_text

app = FastAPI(title="AI Document Assistant")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class AnswerResponse(BaseModel):
    question: str
    answer: str


@app.get("/health")
def health():
    """Simple check that the server is running."""
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
def ask_document(file: UploadFile = File(...), question: str = Form(...)):
    """Upload a PDF and ask a question about it."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large (max 10 MB).")

    document_text = extract_text(BytesIO(contents))
    answer = ask(document_text, question)

    return AnswerResponse(question=question, answer=answer)