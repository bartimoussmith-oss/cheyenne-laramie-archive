import hashlib, html, json, re, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

MAX_RESULTS = 50

def locate(text, terms):
    hits = []
    for term in terms:
        pattern = r'(?<!\w)' + re.escape(term).replace(r'\ ', r'\s+') + r'(?!\w)'
        for match in re.finditer(pattern, text, re.I):
            hits.append((match.start(), match.end(), term))
            if len(hits) >= 100:
                return sorted(hits)
    return sorted(hits)

def revision():
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None

def main():
    started = time.monotonic()
    profiles = json.loads(Path('osint/profiles.json').read_text())['profiles']
    sources = {}
    if Path('ledger.jsonl').exists():
        for line in Path('ledger.jsonl').read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            if row.get('disposition') == 'captured' and re.fullmatch('[0-9a-f]{64}', row.get('sha256', '')) and urlsplit(row.get('url', '')).scheme == 'https':
                sources.setdefault(row['sha256'], row)
    results = {p['id']: [] for p in profiles}
    counts = {p['id']: 0 for p in profiles}
    files = sorted(Path('text').glob('*.txt')) + sorted(Path('derived').glob('*/page-*.json'))
    scanned, errors, indexed_hashes = 0, [], set()
    rev = revision()
    for path in files:
        if scanned >= 20000 or time.monotonic() - started > 120:
            break
        scanned += 1
        try:
            if path.stat().st_size > 2100000:
                raise ValueError('representation exceeds analysis bound')
            if path.suffix == '.json':
                item = json.loads(path.read_text(encoding='utf-8'))
                digest, text, page = item['source_sha256'], item['text'], item['page']
                method = item.get('method', 'unknown')
            else:
                digest, text, page, method = path.stem, path.read_text(encoding='utf-8'), None, 'html_text'
            if digest not in sources:
                continue
            indexed_hashes.add(digest)
            row = sources[digest]
            for profile in profiles:
                hits = locate(text, profile['terms'])
                if not hits or (profile.get('require_any') and not locate(text, profile['require_any'])):
                    continue
                counts[profile['id']] += 1
                if len(results[profile['id']]) >= MAX_RESULTS:
                    continue
                passages = []
                for a, b, term in hits[:3]:
                    left, right = max(0, a - 150), min(len(text), b + 250)
                    passages.append({'term': term, 'match_start': a, 'match_end': b, 'passage_start': left, 'passage_end': right, 'text': text[left:right]})
                original = 'objects/' + digest[:2] + '/' + digest
                prefix = 'https://github.com/bartimoussmith-oss/cheyenne-laramie-archive/blob/' + rev + '/' if rev else None
                results[profile['id']].append({'classification': 'unreviewed_topical_match_not_a_finding', 'source_sha256': digest, 'source_url': row['url'], 'source_retrieved_at': row.get('retrieved_at'), 'page': page, 'extraction_method': method, 'quality_verified': False, 'representation_path': path.as_posix(), 'representation_text_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(), 'representation_permalink': prefix + path.as_posix() if prefix else None, 'original_permalink': prefix + original if prefix else None, 'evidence': passages})
        except Exception as exc:
            if len(errors) < 50:
                errors.append({'path': path.as_posix(), 'error': str(exc)[:300]})
    out = Path('osint/results')
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    now = datetime.now(timezone.utc).isoformat()
    for profile in profiles:
        key = profile['id']
        payload = {'profile': key, 'title': profile['title'], 'generated_at': now, 'source_revision': rev, 'classification': 'retrieval_triage_not_investigative_findings', 'matched_representations': counts[key], 'exported_representations': len(results[key]), 'result_cap': MAX_RESULTS, 'results_truncated': counts[key] > MAX_RESULTS, 'results': results[key]}
        (out / (key + '.json')).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        lines = ['# ' + profile['title'], '', 'Unreviewed topic matches only. These are not allegations, verified findings or proof of wrongdoing.', '', 'Matched representations: %s; exported: %s. Deterministic file order, not importance ranking.' % (counts[key], len(results[key])), '']
        for item in results[key]:
            lines.extend(['## Source ' + item['source_sha256'][:16] + (' — page ' + str(item['page']) if item['page'] else ''), '', 'Publisher: ' + item['source_url'], ''])
            if item['representation_permalink']:
                lines.extend(['Preserved representation: ' + item['representation_permalink'], ''])
            for passage in item['evidence']:
                lines.extend(['> ' + html.escape(passage['text']).replace('\n', '\n> '), ''])
        (out / (key + '.md')).write_text('\n'.join(lines), encoding='utf-8')
        summary.append({'profile': key, 'matches': counts[key], 'exported': len(results[key])})
    (out / 'status.json').write_text(json.dumps({'generated_at': now, 'source_revision': rev, 'available_representation_files': len(files), 'scanned_files': scanned, 'scan_truncated': scanned < len(files), 'unique_source_objects_with_indexed_text': len(indexed_hashes), 'captured_source_objects_in_ledger': len(sources), 'errors_first_50': errors, 'full_historical_coverage': False, 'profiles': summary}, indent=2))
    if sum(p.stat().st_size for p in out.glob('*') if p.is_file()) > 5000000:
        raise RuntimeError('OSINT output exceeds publication budget; do not publish')

if __name__ == '__main__':
    main()
