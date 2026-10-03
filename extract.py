import sys
from pypdf import PdfReader


def extract_pages(pdf) -> list[str]:
    """Return a list with the text of each page (index 0 = page 1)."""
    reader = PdfReader(pdf)
    return [page.extract_text() or "" for page in reader.pages]


def extract_text(pdf) -> str:
    """Return all text in one string, labelled by page."""
    pages = extract_pages(pdf)
    return "\n\n".join(
        f"--- Page {number} ---\n{text}" for number, text in enumerate(pages, start=1)
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract.py <path-to-pdf>")
        sys.exit(1)

    text = extract_text(sys.argv[1])
    print(text[:2000])
    print(f"\nTotal characters extracted: {len(text)}")