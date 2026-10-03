import sys

import anthropic
from dotenv import load_dotenv

from extract import extract_text

load_dotenv()  # reads ANTHROPIC_API_KEY from .env

client = anthropic.Anthropic()  # picks up the key automatically

MODEL = "claude-sonnet-5-5"

SYSTEM_PROMPT = """You are a study assistant. Answer the question using only the document provided.
If the answer isn't in the document, say so clearly instead of guessing.
When possible, mention which page the information came from."""


def ask(document_text: str, question: str) -> str:
    """Send the document and question to Claude and return the answer."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"<document>\n{document_text}\n</document>\n\nQuestion: {question}",
            }
        ],
    )
    # The response is a list of blocks (e.g. thinking, then text); keep only the text
    return "".join(block.text for block in response.content if block.type == "text")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: python ask.py <path-to-pdf> "<your question>"')
        sys.exit(1)

    pdf_path, question = sys.argv[1], sys.argv[2]
    document_text = extract_text(pdf_path)
    print(ask(document_text, question))