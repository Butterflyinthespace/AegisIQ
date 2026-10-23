
"""AegisIQ — Connect document extraction to ECC evidence mapping."""

from io import BytesIO

from document_processor import extract_document
from evidence_mapper import map_evidence


def run_assessment(uploaded_files):
    """
    Extract text from uploaded evidence documents and map
    potentially relevant evidence to verified ECC controls.

    Note: Keyword matches are not compliance conclusions.
    """
    documents = []
    extraction_errors = []

    for uploaded_file in uploaded_files:
        filename = getattr(uploaded_file, "name", "unknown_file")

        try:
            result = extract_document(uploaded_file)

            if not isinstance(result, dict):
                raise ValueError(
                    "Expected a structured extraction dictionary."
                )

            # The document processor returns content in sections:
            # {
            #     "sections": [
            #         {"source": "Text", "text": "..."}
            #     ],
            #     "characters": 123,
            #     ...
            # }
            sections = result.get("sections", [])

            if not isinstance(sections, list):
                raise ValueError(
                    "Extractor returned an invalid sections format."
                )

            text_parts = []

            for section in sections:
                if not isinstance(section, dict):
                    continue

                section_text = section.get("text", "")
                section_source = section.get("source", "Unknown")

                if not isinstance(section_text, str):
                    continue

                if section_text.strip():
                    text_parts.append(
                        f"[Source: {section_source}]\n"
                        f"{section_text}"
                    )

            extracted_text = "\n\n".join(text_parts)

            if not extracted_text.strip():
                raise ValueError(
                    "No readable text extracted from document."
                )

            # Preserve the original character count from
            # document_processor.py for accurate reporting.
            original_characters = result.get(
                "characters",
                len(extracted_text),
            )

            documents.append({
                "filename": filename,
                "text": extracted_text,
                "characters": original_characters,
                "sections": sections,
                "format": result.get("format", "Unknown"),
                "truncated": result.get("truncated", False),
                "empty": result.get("empty", False),
                "extraction_metadata": result,
            })

        except Exception as exc:
            extraction_errors.append({
                "filename": filename,
                "error": str(exc),
            })

    # Map only successfully extracted documents.
    # The mapper returns potential matches requiring review.
    mappings = map_evidence(documents)

    return {
        "documents_processed": len(documents),
        "documents": documents,
        "mappings": mappings,
        "extraction_errors": extraction_errors,
    }


if __name__ == "__main__":
    print("AegisIQ — End-to-End Pipeline Test")

    # Fictional hospital evidence created entirely in memory.
    sample_text = (
        "Noura Valley Hospital Cybersecurity Strategy\n"
        "The hospital maintains a cybersecurity strategy "
        "with an action plan and strategic objectives.\n"
        "This document is fictional test evidence."
    )

    sample = BytesIO(sample_text.encode("utf-8"))
    sample.name = "fictional_hospital_strategy.txt"

    result = run_assessment([sample])

    print(
        "Documents processed:",
        result["documents_processed"],
    )
    print(
        "Extraction errors:",
        result["extraction_errors"],
    )

    for document in result["documents"]:
        print("Filename:", document["filename"])
        print("Format:", document["format"])
        print("Characters:", document["characters"])
        print("Sections:", len(document["sections"]))
        print(
            "Extracted preview:",
            repr(document["text"][:180]),
        )

    for mapping in result["mappings"]:
        print("Control:", mapping["control_id"])
        print(
            "Potential matches:",
            len(mapping["potential_evidence"]),
        )
        print("Status:", mapping["assessment_status"])
