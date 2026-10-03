import sys
from pypdf import PdfReader


def extract_text(pdf_path: str) -> str:
    """Read a PDF and return all its text, labelled by page."""
    reader = PdfReader(pdf_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(f"--- Page {page_number} ---\n{text}")

    return "\n\n".join(pages)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract.py <path-to-pdf>")
        sys.exit(1)

    text = extract_text(sys.argv[1])
    print(text[:2000])
    print(f"\nTotal characters extracted: {len(text)}")