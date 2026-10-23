"""AegisIQ — transparent, keyword-based evidence discovery (NOT AI scoring)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTROLS_PATH = ROOT / 'frameworks' / 'ecc_pilot_controls.json'

# Phrases are discovery hints, not compliance tests or regulatory wording.
CONTROL_KEYWORDS = {
    '1-1-2': ['cybersecurity strategy', 'action plan', 'strategic objectives', 'implementation plan'],
    '2-2-3': ['access review', 'access rights', 'privileged', 'mfa', 'multi-factor', 'multifactor', 'least privilege', 'terminated', 'account status', 'user role', 'authorization'],
    '2-9-3': ['backup', 'restore', 'recovery', 'restoration', 'rpo', 'rto'],
    '2-12-3': ['siem', 'security event', 'event log', 'log retention', 'monitoring', 'alert rule', 'audit log', 'log source'],
}


def _excerpt(text, phrase, radius=125):
    position = text.casefold().find(phrase.casefold())
    if position < 0:
        return text[:250]
    start = max(0, position - radius)
    end = min(len(text), position + len(phrase) + radius)
    return ('…' if start else '') + text[start:end].strip() + ('…' if end < len(text) else '')


def map_evidence(evidence_documents):
    controls = json.loads(CONTROLS_PATH.read_text(encoding='utf-8'))
    results = []
    for control in controls:
        control_id = control['control_id']
        phrases = CONTROL_KEYWORDS.get(control_id, [])
        matches = []
        for document in evidence_documents:
            # Prefer section-level provenance; fall back to combined text.
            sections = document.get('sections')
            if not isinstance(sections, list) or not sections:
                sections = [{'source': 'Document', 'text': document.get('text', '')}]
            for section in sections:
                if not isinstance(section, dict):
                    continue
                content = section.get('text', '')
                if not isinstance(content, str) or not content.strip():
                    continue
                found = [p for p in phrases if p.casefold() in content.casefold()]
                if found:
                    matches.append({
                        'filename': document.get('filename', 'Unknown'),
                        'source': str(section.get('source', 'Unknown')),
                        'matched_keywords': found,
                        'match_count': len(found),
                        'evidence_excerpt': _excerpt(content, found[0]),
                    })
        results.append({
            'control_id': control_id,
            'requirement': control['requirement'],
            'pdf_page': control['pdf_page'],
            'source_pages': control.get('source_pages', [control['pdf_page']]),
            'subrequirements': control.get('subrequirements', []),
            'potential_evidence': matches,
            'assessment_status': 'requires_human_review',
        })
    return results


if __name__ == '__main__':
    sample = [{'filename': 'fictional_MFA.csv', 'sections': [{'source': 'CSV row 1', 'text': 'Privileged administrator MFA disabled'}]}]
    for result in map_evidence(sample):
        print(result['control_id'], 'matches:', len(result['potential_evidence']))
