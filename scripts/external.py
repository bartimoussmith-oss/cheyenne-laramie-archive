import hashlib, json, posixpath, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote, parse_qsl
import adapters

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        keys = {'a': 'href', 'iframe': 'src', 'embed': 'src', 'object': 'data', 'video': 'src', 'audio': 'src', 'source': 'src', 'track': 'src'}
        if tag in keys and attrs.get(keys[tag]):
            self.urls.append(attrs[keys[tag]])

def permitted(url, config):
    p = urlsplit(url)
    if p.scheme != 'https' or p.username or p.password or p.port not in (None, 443):
        return False
    if len(url) > 2048 or len(parse_qsl(p.query)) > 6:
        return False
    path = posixpath.normpath(unquote(p.path))
    for rule in config['scopes']:
        if p.hostname == rule['host']:
            if rule.get('path_prefix') and (path + '/').startswith(rule['path_prefix']):
                return True
            if urlunsplit((p.scheme, p.netloc, p.path, p.query, '')) in rule.get('exact_urls', []):
                return True
    return False

def append(row):
    row['retrieved_at'] = datetime.now(timezone.utc).isoformat()
    with open('ledger.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')

def main():
    config = json.loads(Path('external-sources.json').read_text())
    state_path = Path('external-state.json')
    state = json.loads(state_path.read_text()) if state_path.exists() else {'queue': [[u, None] for u in config['seeds']], 'seen': []}
    queue, seen = state['queue'], set(state['seen'])
    queued = {r[0] for r in queue}
    fetcher = adapters.Fetcher(config)
    started, captured, failures = time.monotonic(), 0, [],
    storage = sum(p.stat().st_size for folder in ('objects', 'text', 'derived') for p in Path(folder).rglob('*') if p.is_file())
    paused = False
    while queue and fetcher.remaining > 1 and time.monotonic() - started < 600:
        url, parent = queue.pop(0)
        queued.discard(url)
        if url in seen:
            continue
        if not permitted(url, config):
            append({'url': url, 'parent': parent, 'disposition': 'external_review', 'collector': 'scoped-external-v1'})
            seen.add(url)
            continue
        if storage + 45000000 > 350000000:
            queue.insert(0, [url, parent])
            paused = True
            break
        try:
            data = fetcher.get(url)
            start = data.lstrip()[:4096].lower()
            if data.startswith(b'%PDF-'):
                mime = 'application/pdf'
            elif start.startswith((b'{', b'[')):
                mime = 'application/json'
            elif b'<html' in start or b'<!doctype html' in start:
                mime = 'text/html'
                if b'<title>access denied' in start or b'<title>just a moment' in start:
                    raise ValueError('Access challenge; not a source record')
            elif any(urlsplit(url).path.lower().endswith(x) for x in ('.mp4', '.mp3', '.wav', '.webm', '.vtt', '.srt')):
                mime = 'application/octet-stream'
            else:
                raise ValueError('Unverified format; retained URL as gap')
            digest = hashlib.sha256(data).hexdigest()
            target = Path('objects') / digest[:2] / digest
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(data)
                storage += len(data)
            append({'url': url, 'parent': parent, 'disposition': 'captured', 'sha256': digest, 'bytes': len(data), 'media_type': mime, 'object_path': str(target), 'collector': 'scoped-external-v1'})
            captured += 1
            if mime == 'text/html':
                parser = Links()
                parser.feed(data.decode('utf-8', 'replace'))
                for link in parser.urls:
                    p = urlsplit(urljoin(url, link))
                    child = urlunsplit((p.scheme, p.netloc, p.path, p.query, ''))
                    if child not in queued and child not in seen:
                        queue.append([child, url])
                        queued.add(child)
            seen.add(url)
        except RuntimeError:
            queue.insert(0, [url, parent])
            break
        except Exception as exc:
            error = str(exc)[:500]
            append({'url': url, 'parent': parent, 'disposition': 'failed_or_review', 'error': error, 'collector': 'scoped-external-v1'})
            failures.append({'url': url, 'error': error})
            seen.add(url)
    state_path.write_text(json.dumps({'queue': queue, 'seen': sorted(seen)}, indent=2))
    adapters.save(Path('.'), 'external-status.json', {'updated_at': datetime.now(timezone.utc).isoformat(), 'captured_this_run': captured, 'pending_urls': len(queue), 'failures_this_run': failures, 'storage_pause': paused, 'complete': False, 'javascript_forms_supported': False, 'gis_features_exported': False, 'repositories_created': False})

if __name__ == '__main__':
    main()
