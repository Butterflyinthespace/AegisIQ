
"""AegisIQ — position-based ECC control extraction.

Produces draft candidates requiring verification before assessment.
"""

import json
import re
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "frameworks" / "ECC-2-2024.pdf"
OUTPUT = ROOT / "frameworks" / "ecc_controls_structured.json"

# Recognize 3-part and 4-part identifiers.
ID_PATTERN = re.compile(
    r"(?<![\w.-])([1-5]-\d{1,2}-\d{1,2}(?:-\d{1,2})?)(?![\w.-])"
)

START_PAGE = 16
END_PAGE = 34


def get_lines(page):
    """Extract lines with bounding boxes and vertical coordinates."""
    lines = []

    for block in page.get_text("dict")["blocks"]:
        if "lines" not in block:
            continue

        for line in block["lines"]:
            spans = line["spans"]
            text = "".join(span["text"] for span in spans).strip()

            if text:
                lines.append({
                    "text": text,
                    "x": min(span["bbox"][0] for span in spans),
                    "y": min(span["bbox"][1] for span in spans),
                })

    return sorted(lines, key=lambda item: (item["y"], item["x"]))


def extract():
    candidates = []

    with pymupdf.open(PDF) as document:
        for page_index in range(START_PAGE - 1, END_PAGE):
            page = document[page_index]
            lines = get_lines(page)

            for index, line in enumerate(lines):
                matches = list(ID_PATTERN.finditer(line["text"]))

                for match in matches:
                    # IDs in the control-number column are more likely
                    # to represent actual requirements.
                    if not 65 <= line["x"] <= 165:
                        continue

                    control_id = match.group(1)
                    next_id_y = page.rect.height - 65

                    for later in lines[index + 1:]:
                        if (
                            later["y"] > line["y"] + 2
                            and 65 <= later["x"] <= 165
                            and ID_PATTERN.search(later["text"])
                        ):
                            next_id_y = later["y"]
                            break

                    requirement_lines = [
                        other["text"]
                        for other in lines
                        if line["y"] - 3 <= other["y"] < next_id_y
                        and other["x"] >= 150
                        and other["y"] < page.rect.height - 55
                    ]

                    candidates.append({
                        "control_id": control_id,
                        "pdf_page": page_index + 1,
                        "requirement_draft": " ".join(
                            requirement_lines
                        ).strip(),
                        "verification_status": "unverified",
                    })

    return candidates


if __name__ == "__main__":
    result = extract()

    OUTPUT.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    ids = [item["control_id"] for item in result]

    print("Structured candidates:", len(result))
    print("Unique IDs:", len(set(ids)))
    print("Empty descriptions:", sum(
        not item["requirement_draft"] for item in result
    ))
    print("Saved to:", OUTPUT)

    print("\nFirst five candidates:")
    for item in result[:5]:
        print(
            item["control_id"],
            "| Page", item["pdf_page"],
            "|", item["requirement_draft"][:130],
        )
