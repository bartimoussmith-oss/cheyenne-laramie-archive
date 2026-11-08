import argparse, hashlib, ipaddress, json, socket, subprocess, time
from pathlib import Path
from urllib.parse import urlsplit, urljoin, urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.robotparser import RobotFileParser
from html.parser import HTMLParser

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class Fetcher:
    def __init__(self, job):
        if job.get('approved_for_copy') is not True or not job.get('rights_basis'):
            raise ValueError('Explicit copying approval and rights basis required')
        self.hosts = set(job['allowed_hosts'])
        self.remaining = 100
        self.robots = {}
        self.last = 0
        self.opener = build_opener(NoRedirect())
    def raw(self, url, limit=45000000):
        p = urlsplit(url)
        if p.scheme != 'https' or p.hostname not in self.hosts or p.username or p.password or p.port not in (None, 443):
            raise ValueError('URL outside approved HTTPS hosts')
        for item in socket.getaddrinfo(p.hostname, 443):
            if not ipaddress.ip_address(item[4][0]).is_global:
                raise ValueError('Nonpublic address')
        if self.remaining <= 0:
            raise RuntimeError('Request budget exhausted; retain partial outputs')
        time.sleep(max(0, 2 - (time.monotonic() - self.last)))
        self.remaining -= 1
        self.last = time.monotonic()
        with self.opener.open(Request(url, headers={'User-Agent': 'CheyenneLaramieArchive/0.2'}), timeout=45) as r:
            data = r.read(limit + 1)
            if len(data) > limit:
                raise ValueError('Oversized response')
            return data
    def get(self, url):
        host = urlsplit(url).hostname
        if host not in self.robots:
            rp = RobotFileParser()
            rp.parse(self.raw('https://' + host + '/robots.txt', 1000000).decode('utf-8', 'replace').splitlines())
            self.robots[host] = rp
        rp = self.robots[host]
        if not rp.can_fetch('CheyenneLaramieArchive', url):
            raise ValueError('Robots denied')
        time.sleep(max(0, (rp.crawl_delay('*') or 2) - (time.monotonic() - self.last)))
        return self.raw(url)
    def json(self, url):
        data = json.loads(self.get(url))
        if isinstance(data, dict) and 'error' in data:
            raise ValueError(str(data['error']))
        return data

def save(out, name, data):
    p = out / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False, indent=2).encode())
    return {'path': name, 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

def gis(job, out):
    f = Fetcher(job)
    base = job['layer_url'].rstrip('/')
    save(out, 'layer.json', f.json(base + '?f=json'))
    ids = f.json(base + '/query?' + urlencode({'f': 'json', 'where': '1=1', 'returnIdsOnly': 'true'}))
    save(out, 'object-ids.json', ids)
    expected = sorted(set(ids.get('objectIds') or []))
    field = ids.get('objectIdFieldName')
    if not field:
        raise ValueError('No object ID field; export cannot be verified')
    obtained = set()
    for offset in range(0, len(expected), 100):
        batch = expected[offset:offset + 100]
        data = f.json(base + '/query?' + urlencode({'f': 'json', 'objectIds': ','.join(map(str, batch)), 'outFields': '*', 'returnGeometry': 'true'}))
        save(out, 'features/%08d.json' % offset, data)
        actual = {x['attributes'][field] for x in data.get('features', [])}
        obtained.update(actual)
        if actual != set(batch) or data.get('exceededTransferLimit'):
            raise ValueError('Feature batch incomplete; retained partial export')
    final = f.json(base + '/query?' + urlencode({'f': 'json', 'where': '1=1', 'returnIdsOnly': 'true'}))
    stable = set(final.get('objectIds') or []) == set(expected)
    save(out, 'coverage.json', {'expected': len(expected), 'obtained': len(obtained), 'id_set_stable': stable, 'complete': stable and obtained == set(expected), 'format': 'Esri JSON', 'attribute_snapshot_atomic': False})

def legistar(job, out):
    f = Fetcher(job)
    base = job['events_api'].rstrip('/')
    offset = int(job.get('offset', 0))
    while True:
        events = f.json(base + '?' + urlencode({'$top': 100, '$skip': offset, '$orderby': 'EventId asc'}))
        if not isinstance(events, list):
            raise ValueError('Expected event list')
        save(out, 'events/%08d.json' % offset, events)
        links = []
        for event in events:
            for key in ('EventAgendaFile', 'EventMinutesFile', 'EventVideoPath', 'EventAgendaPacketFile'):
                if event.get(key):
                    links.append({'event_id': event['EventId'], 'field': key, 'url': event[key]})
        save(out, 'links/%08d.json' % offset, links)
        offset += len(events)
        save(out, 'checkpoint.json', {'next_offset': offset, 'event_enumeration_complete': len(events) < 100, 'attachments_complete': False})
        if len(events) < 100:
            return

def media(job, out):
    f = Fetcher(job)
    rows = []
    for i, url in enumerate(job['direct_download_urls']):
        data = f.get(url)
        row = save(out, 'originals/%04d.bin' % i, data)
        rows.append({'source_url': url, **row})
        save(out, 'manifest.json', rows)

def ocr(job, out):
    source = Path(job['local_pdf']).resolve()
    text = out / 'native.txt'
    subprocess.run(['pdftotext', '-layout', str(source), str(text)], check=True, timeout=300)
    if len(text.read_text(errors='replace').strip()) >= 100:
        save(out, 'ocr-status.json', {'method': 'native_pdftotext', 'quality_verified': False})
        return
    images = out / 'pages'
    images.mkdir(exist_ok=True)
    first, last = int(job.get('first_page', 1)), int(job.get('last_page', 10))
    if first < 1 or last < first or last - first > 19:
        raise ValueError('OCR job limited to 20 pages')
    subprocess.run(['pdftoppm', '-f', str(first), '-l', str(last), '-r', '150', '-png', str(source), str(images / 'page')], check=True, timeout=300)
    for image in sorted(images.glob('*.png')):
        subprocess.run(['tesseract', str(image), str(image.with_suffix('')), '-l', 'eng', 'txt'], check=True, timeout=180)
    save(out, 'ocr-status.json', {'method': 'tesseract', 'requested_pages': [first, last], 'whole_document_complete': False, 'quality_verified': False})

def partition(job, out):
    root = Path(job['local_root']).resolve()
    cap = int(job.get('partition_bytes', 350000000))
    if cap <= 0:
        raise ValueError('Invalid partition budget')
    shards, current, used = [], [], 0
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.is_symlink():
            continue
        size = p.stat().st_size
        if size > 45000000:
            raise ValueError('Oversized object requires separately approved lossless chunking')
        if size > cap:
            raise ValueError('Object exceeds shard cap')
        if current and used + size > cap:
            shards.append(current)
            current, used = [], 0
        current.append({'path': str(p.relative_to(root)), 'bytes': size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
        used += size
    if current:
        shards.append(current)
    save(out, 'partition-plan.json', {'proposed_partitions': [{'name': 'cheyenne-laramie-data-%03d' % (i + 1), 'files': rows} for i, rows in enumerate(shards)], 'published': False, 'repositories_created': False})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['gis', 'legistar', 'media', 'ocr', 'partition'])
    parser.add_argument('job')
    parser.add_argument('output')
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    globals()[args.mode](json.loads(Path(args.job).read_text()), out)

if __name__ == '__main__':
    main()
