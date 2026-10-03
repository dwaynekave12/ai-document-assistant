import uuid

from fastapi.testclient import TestClient

import main
from chunker import Chunk

client = TestClient(main.app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_rejects_non_pdf():
    response = client.post(
        "/documents",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Please upload a PDF file."


def test_ask_with_invalid_id_returns_422():
    response = client.post("/documents/not-a-uuid/ask", json={"question": "hi"})

    assert response.status_code == 422


def test_ask_unknown_document_returns_404(monkeypatch):
    monkeypatch.setattr(main, "document_exists", lambda document_id: False)

    response = client.post(f"/documents/{uuid.uuid4()}/ask", json={"question": "hi"})

    assert response.status_code == 404


def test_ask_returns_answer_and_sources(monkeypatch):
    monkeypatch.setattr(main, "document_exists", lambda document_id: True)
    monkeypatch.setattr(
        main,
        "answer_question",
        lambda retriever, question: ("Fake answer", [(Chunk(text="x", page=3), 0.91234)]),
    )

    response = client.post(f"/documents/{uuid.uuid4()}/ask", json={"question": "hi"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Fake answer",
        "sources": [{"page": 3, "score": 0.912}],
    }