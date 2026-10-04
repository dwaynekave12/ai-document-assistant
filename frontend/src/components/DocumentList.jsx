import { useEffect, useState } from "react";
import { deleteDocument, listDocuments } from "../api";

function DocumentList({ onSelect }) {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    listDocuments()
      .then((docs) => setDocuments(docs))
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  async function handleDelete(documentId) {
    if (!window.confirm("Delete this document? This can't be undone.")) return;

    try {
      await deleteDocument(documentId);
      setDocuments((previous) => previous.filter((doc) => doc.document_id !== documentId));
    } catch (err) {
      setError(err.message);
    }
  }

  if (isLoading) {
    return <p className="thinking">Loading your documents...</p>;
  }

  return (
    <section className="card">
      <h2>Your documents</h2>
      {error && <p className="error">{error}</p>}

      {documents.length === 0 ? (
        <p>No documents yet. Upload one above.</p>
      ) : (
        <ul className="document-list">
          {documents.map((doc) => (
            <li key={doc.document_id}>
              <button className="link-button" onClick={() => onSelect(doc)}>
                {doc.filename}
              </button>
              <span className="meta">
                {doc.pages} pages · {new Date(doc.created_at).toLocaleDateString()}
              </span>
              <button className="delete-button" onClick={() => handleDelete(doc.document_id)}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default DocumentList;