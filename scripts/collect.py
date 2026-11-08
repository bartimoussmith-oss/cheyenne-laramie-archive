import hashlib, ipaddress, json, os, socket, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.robotparser import RobotFileParser

ROOT = Path('.')
STATE = ROOT / 'state.json'
UA = 'CheyenneLaramiePublicArchive/0.1 (+https://github.com/bartimoussmith-oss/cheyenne-laramie-archive)'
LIMIT = 20_000_000
BUDGET = 400_000_000
MAX_REQUESTS = 120
started = time.monotonic()
requests = 0
last = 0.0
config = json.loads(Path('sources.json').read_text())
allowed = set(config['allowed_hosts'])
state = json.loads(STATE.read_text()) if STATE.exists() else {'queue': [[u, None] for u in config['seeds']], 'seen': []}
seen = set(state['seen'])
queue = state['queue']
queued = {x[0] for x in queue}
robots = {}
run_id = os.getenv('GITHUB_RUN_ID', 'local')

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = build_opener(NoRedirect())

def stamp():
    return datetime.now(timezone.utc).isoformat()

def log(**row):
    with open('ledger.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps({'retrieved_at': stamp(), 'run_id': run_id, **row}, ensure_ascii=False) + '\n')

def normalize(url):
    p = urlsplit(url)
    if p.scheme != 'https' or p.username or p.password or p.port not in (None, 443):
        raise ValueError('unsupported URL')
    if len(url) > 2048 or len(parse_qsl(p.query)) > 6:
        raise ValueError('query budget')
    return urlunsplit(('https', p.netloc.lower(), p.path or '/', p.query, ''))

def fetch(url, limit):
    global requests, last
    p = urlsplit(url)
    if p.hostname not in allowed:
        raise ValueError('host outside allowlist')
    for addr in socket.getaddrinfo(p.hostname, 443):
        if not ipaddress.ip_address(addr[4][0]).is_global:
            raise ValueError('non-public address')
    if requests >= MAX_REQUESTS or time.monotonic() - started > 900:
        raise RuntimeError('run budget reached')
    time.sleep(max(0, 2 - (time.monotonic() - last)))
    requests += 1
    last = time.monotonic()
    with opener.open(Request(url, headers={'User-Agent': UA}), timeout=30) as response:
        length = response.headers.get('Content-Length')
        if length and int(length) > limit:
            raise ValueError('oversized object')
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError('oversized object')
        return data, dict(response.headers.items())

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.text = [], []
        self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        attrs = dict(attrs)
        if tag in ('a', 'iframe') and (attrs.get('href') or attrs.get('src')):
            self.links.append(attrs.get('href') or attrs.get('src'))
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)
    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.text.append(data.strip())

objects = Path('objects')
objects.mkdir(exist_ok=True)
used = sum(p.stat().st_size for p in objects.rglob('*') if p.is_file())
while queue and requests < MAX_REQUESTS and time.monotonic() - started < 900:
    url, parent = queue.pop(0)
    queued.discard(url)
    if url in seen:
        continue
    if used + LIMIT > BUDGET:
        queue.insert(0, [url, parent])
        log(url=url, disposition='partition_required', bytes_used=used)
        break
    try:
        url = normalize(url)
        host = urlsplit(url).hostname
        if host not in allowed:
            log(url=url, parent=parent, disposition='external_review')
            seen.add(url)
            continue
        if host not in robots:
            body, _ = fetch('https://' + host + '/robots.txt', 1_000_000)
            parser = RobotFileParser()
            parser.parse(body.decode('utf-8', 'replace').splitlines())
            robots[host] = parser
        parser = robots[host]
        if not parser.can_fetch(UA, url):
            raise ValueError('robots denied')
        delay = parser.crawl_delay(UA) or parser.crawl_delay('*') or 2
        time.sleep(max(0, delay - (time.monotonic() - last)))
        body, headers = fetch(url, LIMIT)
        mime = next((v for k, v in headers.items() if k.lower() == 'content-type'), '').lower()
        if not any(x in mime for x in ('text/html', 'application/pdf', 'text/plain', 'text/csv', 'application/json', 'spreadsheet', 'excel', 'wordprocessing', 'msword')):
            raise ValueError('unsupported media type: ' + mime)
        digest = hashlib.sha256(body).hexdigest()
        directory = objects / digest[:2]
        directory.mkdir(exist_ok=True)
        target = directory / digest
        if not target.exists():
            target.write_bytes(body)
            used += len(body)
        log(url=url, parent=parent, disposition='captured', sha256=digest, bytes=len(body), media_type=mime, object_path=str(target))
        if 'text/html' in mime:
            page = Page()
            page.feed(body.decode('utf-8', 'replace'))
            text_dir = Path('text')
            text_dir.mkdir(exist_ok=True)
            (text_dir / (digest + '.txt')).write_text('\n'.join(page.text), encoding='utf-8')
            for link in page.links:
                try:
                    child = normalize(urljoin(url, link))
                except (ValueError, TypeError):
                    continue
                if child not in seen and child not in queued:
                    queue.append([child, url])
                    queued.add(child)
        seen.add(url)
    except RuntimeError:
        queue.insert(0, [url, parent])
        break
    except Exception as exc:
        log(url=url, parent=parent, disposition='failed_or_review', error=str(exc)[:500])
        seen.add(url)

STATE.write_text(json.dumps({'queue': queue, 'seen': sorted(seen)}, indent=2))
Path('status.json').write_text(json.dumps({'schema': 'archive-status-v1', 'updated_at': stamp(), 'run_id': run_id, 'requests_this_run': requests, 'seen_urls': len(seen), 'pending_urls': len(queue), 'original_object_bytes': used, 'inventory_complete': False, 'historical_coverage_complete': False, 'partition_required': used + LIMIT > BUDGET, 'limitations': config['pending_adapters'], 'failures': 'ledger.jsonl; failed URLs require explicit retry after review'}, indent=2))
