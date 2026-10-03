import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { askQuestion } from "../api";

function formatPages(sources) {
  const pages = [...new Set(sources.map((source) => source.page))].sort((a, b) => a - b);
  return pages.join(", ");
}

function Chat({ document }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) return;

    setIsAsking(true);
    setError("");
    try {
      const result = await askQuestion(document.document_id, trimmed);
      setMessages((previous) => [
        ...previous,
        { question: trimmed, answer: result.answer, sources: result.sources },
      ]);
      setQuestion("");
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAsking(false);
    }
  }

  return (
    <div className="chat">
      {messages.map((message, index) => (
        <div key={index} className="message">
          <p className="question">{message.question}</p>
          <div className="answer">
            <ReactMarkdown>{message.answer}</ReactMarkdown>
            <p className="sources">Pages searched: {formatPages(message.sources)}</p>
          </div>
        </div>
      ))}

      {isAsking && <p className="thinking">Thinking...</p>}
      {error && <p className="error">{error}</p>}

      <form className="ask-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask a question about this document..."
          disabled={isAsking}
        />
        <button type="submit" disabled={isAsking || !question.trim()}>
          Ask
        </button>
      </form>
    </div>
  );
}

export default Chat;