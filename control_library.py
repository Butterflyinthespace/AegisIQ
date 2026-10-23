
"""AegisIQ — ECC control extraction and review."""

import json
import re
from pathlib import Path

from framework_reader import load_framework

OUTPUT = Path(__file__).resolve().parent / "frameworks" / "ecc_controls_draft.json"

# Recognizes control IDs such as 1-1-1 and 2-2-3-1.
CONTROL_ID = re.compile(r"\b([1-5]-\d{1,2}-\d{1,2}(?:-\d{1,2})?)\b")

# PDF text may contain repeated headers, footers and table labels.
NOISE = re.compile(
    r"^(Essential Cybersecurity Controls|"
    r"Document classification:|"
    r"TLP:|"
    r"Objective$|Controls$|"
    r"محدود|ود ﺪح)",
    re.IGNORECASE,
)


def extract_control_candidates():
    framework = load_framework()
    candidates = []

    for page in framework["pages"][15:34]:
        # Preserve line order from the PDF.
        lines = [
            line.strip()
            for line in page["text"].splitlines()
            if line.strip()
        ]

        # This is a candidate extractor, not a final
        # regulatory control parser.
        for index, line in enumerate(lines):
            matches = list(CONTROL_ID.finditer(line))

            for match in matches:
                control_id = match.group(1)

                # Some PDF tables place the control ID
                # before the text; others place it after.
                before = line[:match.start()].strip()
                after = line[match.end():].strip()

                context = []
                if before:
                    context.append(before)
                if after:
                    context.append(after)

                # Capture nearby lines for human review.
                for next_line in lines[index + 1:index + 5]:
                    if CONTROL_ID.search(next_line):
                        break
                    if NOISE.search(next_line):
                        continue
                    context.append(next_line)

                candidates.append({
                    "control_id": control_id,
                    "pdf_page": page["pdf_page"],
                    "context": " ".join(context)[:1500],
                    "verification_status": "unverified",
                })

    return candidates


if __name__ == "__main__":
    candidates = extract_control_candidates()

    OUTPUT.write_text(
        json.dumps(
            candidates,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Control candidates:", len(candidates))
    print("Saved to:", OUTPUT)

    print("\nFirst five candidates:")
    for candidate in candidates[:5]:
        print(
            candidate["control_id"],
            "| PDF page",
            candidate["pdf_page"],
            "|",
            candidate["context"][:110],
        )
