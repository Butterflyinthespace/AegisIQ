"""AegisIQ — explainable, rule-based observations from fictional evidence.

Consumes assessment_pipeline.run_assessment(...)["documents"]. No AI claims,
no automatic regulatory verdicts, and no upload persistence.
"""
from __future__ import annotations

import re
from collections import defaultdict


def _norm(value):
    return str(value or '').strip().casefold()


def _tables(documents):
    """Convert the document processor's pipe-separated sections into rows."""
    tables = []
    for document in documents:
        for section in document.get('sections', []):
            source = str(section.get('source', ''))
            content = section.get('text', '')
            if not isinstance(content, str) or not content.strip():
                continue
            lines = [(n, line) for n, line in enumerate(content.splitlines(), 1)
                     if line.strip() and not line.startswith('[Additional rows omitted]')]
            if not lines or '|' not in lines[0][1]:
                continue
            headers = [cell.strip() for cell in lines[0][1].split('|')]
            if len(headers) < 2:
                continue
            records = []
            for number, line in lines[1:]:
                values = [cell.strip() for cell in line.split('|')]
                if len(values) != len(headers):
                    continue  # Ignore malformed rows; never infer missing cells.
                row = dict(zip(headers, values))
                row['_provenance'] = {
                    'filename': document.get('filename', 'Unknown'),
                    'source': source,
                    'row': number,
                    'excerpt': line[:400],
                }
                records.append(row)
            tables.append({'headers': set(headers), 'rows': records})
    return tables


def _select(tables, required):
    for table in tables:
        if set(required).issubset(table['headers']):
            yield from table['rows']


def analyze_security(documents):
    """Return proposed observations with source references; human review required."""
    tables = _tables(documents)
    observations = []

    def add(code, title, control, explanation, evidence, subject):
        observations.append({
            'observation_id': f'OBS-{len(observations) + 1:03d}',
            'rule_id': code,
            'title': title,
            'subject': subject,
            'ecc_control': control,
            'explanation': explanation,
            'evidence': evidence,
            'status': 'requires_human_review',
            'compliance_verdict': None,
        })

    hr = { _norm(r['Employee ID']): r for r in _select(
        tables, ['Employee ID', 'HR status']) if r.get('Employee ID') }
    accounts = list(_select(tables, ['Employee ID', 'Account state']))
    mfa = list(_select(tables, ['Employee ID', 'Privileged', 'MFA enforced']))
    assets = list(_select(tables, ['Asset ID', 'Monitoring status']))
    backups = list(_select(tables, ['Job ID', 'System', 'Result']))
    restores = list(_select(tables, ['Test ID', 'System', 'Outcome']))

    for account in accounts:
        emp = _norm(account.get('Employee ID'))
        person = hr.get(emp)
        if not person:
            continue
        if _norm(person.get('HR status')) in {'terminated', 'contract ended'} and _norm(account.get('Account state')) in {'enabled', 'active'}:
            add('HR_ACCOUNT_MISMATCH', 'Former worker retains enabled account',
                '2-2-3 (access authorization and review)',
                f"HR status is '{person['HR status']}' while the account is '{account['Account state']}'. Confirm revocation timing and any documented exception.",
                [person['_provenance'], account['_provenance']], emp.upper())

    for entry in mfa:
        if _norm(entry.get('Privileged')) == 'yes' and _norm(entry.get('MFA enforced')) == 'no':
            add('PRIVILEGED_MFA_DISABLED', 'Privileged account without enforced MFA',
                '2-2-3 / 2.2.3.2',
                'The privileged account is recorded with MFA enforced = No. Validate scope, authentication path, and compensating controls.',
                [entry['_provenance']], entry.get('Account', entry.get('Employee ID', 'Unknown')))

    for asset in assets:
        if _norm(asset.get('Monitoring status')) in {'not integrated', 'not monitored', 'disabled'}:
            add('ASSET_MONITORING_GAP', 'Clinical asset not integrated with monitoring',
                '2-12-3 / 2.12.3.1 and 2.12.3.4',
                f"Asset inventory records monitoring status as '{asset['Monitoring status']}'. Confirm asset criticality and alternative logging arrangements.",
                [asset['_provenance']], asset.get('Asset ID', 'Unknown'))

    failed_backups = defaultdict(list)
    failed_restores = defaultdict(list)
    for job in backups:
        if _norm(job.get('Result')) in {'failed', 'failure'}:
            failed_backups[_norm(job.get('System'))].append(job)
    for test in restores:
        if _norm(test.get('Outcome')) in {'failed', 'failure'}:
            failed_restores[_norm(test.get('System'))].append(test)
    for system in sorted(set(failed_backups) | set(failed_restores)):
        evidence = [r['_provenance'] for r in failed_backups[system] + failed_restores[system]]
        details = []
        if failed_backups[system]:
            details.append('a failed backup job')
        if failed_restores[system]:
            details.append('a failed recovery test')
        add('BACKUP_RECOVERY_FAILURE', 'Backup or recovery failure requires investigation',
            '2-9-3 / 2.9.3.2 and 2.9.3.3',
            f"Evidence records {' and '.join(details)}. Confirm remediation, successful retesting, and current recovery capability.",
            evidence, system)

    return {
        'observations': observations,
        'observation_count': len(observations),
        'tables_detected': len(tables),
        'scope_note': 'Rule-based, preliminary observations only. No compliance verdict or AI inference.',
    }


if __name__ == '__main__':
    from io import BytesIO
    from zipfile import ZipFile
    from assessment_pipeline import run_assessment
    from pathlib import Path

    pack = Path(__file__).resolve().parent / 'AegisIQ_OBG_Complete_Simulated_Evidence_Pack.zip'
    if not pack.exists():
        print('Analyzer ready. To run the sample test, place the fictional evidence ZIP beside this file.')
    else:
        uploads = []
        with ZipFile(pack) as archive:
            for filename in archive.namelist():
                if re.match(r'^\d{2}_', filename):
                    file = BytesIO(archive.read(filename))
                    file.name = filename
                    uploads.append(file)
        pipeline = run_assessment(uploads)
        outcome = analyze_security(pipeline['documents'])
        print('Documents:', pipeline['documents_processed'])
        print('Extraction errors:', len(pipeline['extraction_errors']))
        print('Structured tables:', outcome['tables_detected'])
        print('Proposed observations:', outcome['observation_count'])
        for finding in outcome['observations']:
            print(f"{finding['observation_id']} | {finding['rule_id']} | {finding['subject']} | {finding['ecc_control']}")
