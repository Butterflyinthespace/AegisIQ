"""AegisIQ — manually transcribed ECC-2:2024 pilot control register.

The wording below is based on the user-provided extraction of official PDF
pages 22, 23, 27 and 29. Verify against the PDF before external publication.
"""
import json
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent / 'frameworks' / 'ecc_pilot_controls.json'
CONTROLS = [
    {'control_id': '1-1-2', 'requirement': 'The entity shall execute an action plan to apply the cybersecurity strategy.', 'pdf_page': 16, 'verification_status': 'reviewed_against_extracted_pdf_text', 'assessment_status': 'not_assessed', 'evidence_ids': []},
    {'control_id': '2-2-3', 'requirement': 'Cybersecurity requirements for identity and access management of the entity shall include the following as a minimum:', 'pdf_page': 22, 'source_pages': [22, 23], 'subrequirements': [
        {'id': '2.2.3.1', 'text': 'Single-factor authentication based on username and password.'},
        {'id': '2.2.3.2', 'text': 'Multi-factor authentication, and defining the suitable authentication factors and their numbers as well as the suitable authentication techniques based on the result of impact assessment of authentication failure and bypass for remote access and for privileged accounts.'},
        {'id': '2.2.3.3', 'text': 'User authorization based on identity and access control principles (Need-to-Know and Need-to-Use principle, Least Privilege principle, and Segregation of Duties principle).'},
        {'id': '2.2.3.4', 'text': 'Privileged access management.'},
        {'id': '2.2.3.5', 'text': 'Periodic review of identities and access rights.'},
    ], 'verification_status': 'reviewed_against_extracted_pdf_text', 'assessment_status': 'not_assessed', 'evidence_ids': []},
    {'control_id': '2-9-3', 'requirement': 'Cybersecurity requirements for backup and recovery management shall include the following as a minimum:', 'pdf_page': 27, 'subrequirements': [
        {'id': '2.9.3.1', 'text': 'Scope of backups to cover critical technology and information assets.'},
        {'id': '2.9.3.2', 'text': 'Ability to perform quick recovery of data and systems after cybersecurity incidents.'},
        {'id': '2.9.3.3', 'text': 'Periodic testing for the effectiveness of backup recovery.'},
    ], 'verification_status': 'reviewed_against_extracted_pdf_text', 'assessment_status': 'not_assessed', 'evidence_ids': []},
    {'control_id': '2-12-3', 'requirement': 'Cybersecurity requirements for cybersecurity event logs and monitoring management shall include the following as a minimum:', 'pdf_page': 29, 'subrequirements': [
        {'id': '2.12.3.1', 'text': 'Activation of cybersecurity event logs for critical information assets within the entity.'},
        {'id': '2.12.3.2', 'text': 'Activation of cybersecurity event logs for critical and privileged accounts accessing information assets as well as for remote access events within the entity.'},
        {'id': '2.12.3.3', 'text': 'Identification of Security Information and Event Management (SIEM) techniques required for cybersecurity event logs collection.'},
        {'id': '2.12.3.4', 'text': 'Continuous monitoring of cybersecurity event logs.'},
        {'id': '2.12.3.5', 'text': 'Retention period of cybersecurity event logs (shall be at least 12 months).'},
    ], 'verification_status': 'reviewed_against_extracted_pdf_text', 'assessment_status': 'not_assessed', 'evidence_ids': []},
]

if __name__ == '__main__':
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(CONTROLS, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Created {len(CONTROLS)} pilot parent controls at {OUTPUT}')
    print('Subrequirements:', sum(len(c.get('subrequirements', [])) for c in CONTROLS))
