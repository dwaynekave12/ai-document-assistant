import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [status, setStatus] = useState("checking...");

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((response) => response.json())
      .then((data) => setStatus(data.status))
      .catch(() => setStatus("cannot reach backend"));
  }, []);

  return (
    <main>
      <h1>AI Document Assistant</h1>
      <p>Backend status: {status}</p>
    </main>
  );
}

export default App;