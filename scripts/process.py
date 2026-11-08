import hashlib, json, re, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
import adapters

def run(command):
    return subprocess.run(command, check=True, capture_output=True, timeout=120)

def captured_pdfs(path):
    rows = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        if row.get('disposition') == 'captured' and 'application/pdf' in row.get('media_type', ''):
            rows.setdefault(row['sha256'], row)
    return rows

def process():
    started = time.monotonic()
    root = Path('derived')
    root.mkdir(exist_ok=True)
    pdfs = captured_pdfs(Path('ledger.jsonl'))
    attempted, failures, pages_written = 0, [], 0
    for digest, row in sorted(pdfs.items()):
        if attempted >= 2 or time.monotonic() - started > 480:
            break
        if not re.fullmatch('[0-9a-f]{64}', digest):
            failures.append({'sha256': digest, 'error': 'invalid hash'})
            continue
        source = Path('objects') / digest[:2] / digest
        directory = root / digest
        directory.mkdir(exist_ok=True)
        try:
            if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
                raise ValueError('Source hash mismatch')
            info = run(['pdfinfo', str(source)]).stdout.decode('utf-8', 'replace')
            match = re.search(r'^Pages:\s+(\d+)', info, re.M)
            if not match:
                raise ValueError('Cannot verify page count')
            count = int(match.group(1))
            missing = [n for n in range(1, count + 1) if not (directory / ('page-%06d.json' % n)).exists()]
            if not missing:
                continue
            attempted += 1
            for number in missing[:4]:
                if time.monotonic() - started > 480:
                    break
                text = run(['pdftotext', '-f', str(number), '-l', str(number), '-layout', str(source), '-']).stdout.decode('utf-8', 'replace')
                method = 'native'
                if len(text.strip()) < 40:
                    prefix = directory / ('render-%06d' % number)
                    image = prefix.with_suffix('.png')
                    try:
                        run(['pdftoppm', '-f', str(number), '-l', str(number), '-singlefile', '-r', '100', '-png', str(source), str(prefix)])
                        if image.stat().st_size > 20000000:
                            raise ValueError('Page image exceeds bounded OCR size')
                        text = run(['tesseract', str(image), 'stdout', '-l', 'eng']).stdout.decode('utf-8', 'replace')
                        method = 'tesseract'
                    finally:
                        image.unlink(missing_ok=True)
                if len(text.encode('utf-8')) > 2000000:
                    raise ValueError('Page text exceeds bounded size')
                adapters.save(directory, 'page-%06d.json' % number, {'source_sha256': digest, 'source_url': row['url'], 'page': number, 'method': method, 'quality_verified': False, 'text': text})
                pages_written += 1
            present = sum((directory / ('page-%06d.json' % n)).exists() for n in range(1, count + 1))
            adapters.save(directory, 'coverage.json', {'source_sha256': digest, 'expected_pages': count, 'extracted_pages': present, 'page_extraction_complete': present == count, 'ocr_accuracy_verified': False})
        except Exception as exc:
            failures.append({'sha256': digest, 'error': str(exc)[:500]})
    proposals = Path('proposals')
    proposals.mkdir(exist_ok=True)
    adapters.partition({'local_root': 'objects', 'partition_bytes': 350000000}, proposals)
    adapters.save(Path('.'), 'derived-status.json', {'updated_at': datetime.now(timezone.utc).isoformat(), 'captured_pdf_objects': len(pdfs), 'pdfs_attempted_this_run': attempted, 'pages_written_this_run': pages_written, 'failures': failures, 'live_processing_complete': False, 'accuracy_verified': False, 'repositories_created': False, 'paid_services_enabled': False})

if __name__ == '__main__':
    process()
