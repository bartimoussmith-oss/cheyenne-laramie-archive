import json
from datetime import datetime, timezone
from pathlib import Path
from process import captured_pdfs

def read(path, default):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else default

def main():
    source = read('state.json', {'queue': []})
    external = read('external-state.json', {'queue': []})
    pdfs = captured_pdfs(Path('ledger.jsonl'))
    pending_pdfs = sum(not read(Path('derived') / digest / 'coverage.json', {}).get('page_extraction_complete', False) for digest in pdfs)
    storage = sum(p.stat().st_size for folder in ('objects', 'text', 'derived') for p in Path(folder).rglob('*') if p.is_file())
    derived_pause = read('derived-status.json', {}).get('derived_storage_pause', False)
    capacity_pause = storage >= 300000000 or derived_pause
    runnable = (bool(source['queue']) or bool(external['queue']) or pending_pdfs > 0) and not capacity_pause
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'pending_government_urls': len(source['queue']), 'pending_external_urls': len(external['queue']), 'pending_pdf_objects': pending_pdfs, 'working_content_bytes': storage, 'capacity_pause': capacity_pause, 'runnable_known_backlog': runnable, 'all_sources_complete': False, 'rights_and_access_gaps_resolved': False}
    Path('continuation-status.json').write_text(json.dumps(result, indent=2))
    print('yes' if runnable else 'no')

if __name__ == '__main__':
    main()
