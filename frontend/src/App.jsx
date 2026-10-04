import { useState } from "react";
import Chat from "./components/Chat";
import UploadForm from "./components/UploadForm";
import "./App.css";
import DocumentList from "./components/DocumentList";

function App() {
  const [document, setDocument] = useState(null);

  return (
    <main className="app">
      <h1>AI Document Assistant</h1>

      {document ? (
        <>
          <div className="document-bar">
            <span>
              Asking about <strong>{document.filename}</strong> ({document.pages} pages)
            </span>
            <button onClick={() => setDocument(null)}>Upload a different PDF</button>
          </div>
          <Chat document={document} />
        </>
            ) : (
        <div className="home">
          <UploadForm onUploaded={setDocument} />
          <DocumentList onSelect={setDocument} />
        </div>
      )}
    </main>
  );
}

export default App;
