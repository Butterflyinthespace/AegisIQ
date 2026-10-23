
"""AegisIQ — Official NCA ECC framework reader."""

from pathlib import Path
import pymupdf


FRAMEWORK_PATH = (
    Path(__file__).resolve().parent
    / "frameworks"
    / "ECC-2-2024.pdf"
)


def load_framework():
    """
    Read the official ECC PDF and preserve page references.

    Returns a dictionary containing document information
    and a list of pages with their extracted text.
    """

    if not FRAMEWORK_PATH.is_file():
        raise FileNotFoundError(
            f"Framework not found: {FRAMEWORK_PATH}"
        )

    pages = []

    with pymupdf.open(FRAMEWORK_PATH) as document:
        for index, page in enumerate(document):
            text = page.get_text("text", sort=True)

            pages.append({
                "pdf_page": index + 1,
                "text": text,
                "characters": len(text),
            })

    return {
        "framework": "NCA ECC-2:2024",
        "filename": FRAMEWORK_PATH.name,
        "total_pages": len(pages),
        "total_characters": sum(
            page["characters"] for page in pages
        ),
        "pages": pages,
    }


if __name__ == "__main__":
    result = load_framework()

    print("Framework:", result["framework"])
    print("Pages:", result["total_pages"])
    print(
        "Characters:",
        result["total_characters"]
    )

    print("\nFirst page preview:")
    print(result["pages"][0]["text"][:500])
