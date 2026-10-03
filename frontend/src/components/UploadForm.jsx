import { useState } from "react";
import { uploadDocument } from "../api";

function UploadForm({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setError("");
    try {
      const uploaded = await uploadDocument(file);
      onUploaded(uploaded);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>Upload a PDF</h2>
      <input
        type="file"
        accept="application/pdf"
        onChange={(event) => setFile(event.target.files[0] ?? null)}
      />
      <button type="submit" disabled={!file || isUploading}>
        {isUploading ? "Processing..." : "Upload"}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}

export default UploadForm;