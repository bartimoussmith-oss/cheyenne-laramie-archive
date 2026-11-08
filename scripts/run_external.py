import json, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import adapters
import external

def event(**row):
    with open('network-events.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps({'time': datetime.now(timezone.utc).isoformat(), **row}) + '\n')

def compliant_get(self, url):
    host = urlsplit(url).hostname
    if host not in self.hosts:
        raise ValueError('Host outside approved scope')
    if host not in self.robots:
        robots_url = 'https://' + host + '/robots.txt'
        parser = RobotFileParser()
        try:
            body = self.raw(robots_url, 1000000)
            parser.parse(body.decode('utf-8', 'replace').splitlines())
            event(stage='robots', url=robots_url, result='parsed')
        except HTTPError as exc:
            if exc.code not in (404, 410):
                event(stage='robots', url=robots_url, result='blocked', status=exc.code)
                raise ValueError('Robots request blocked: %s HTTP %s' % (robots_url, exc.code)) from exc
            body = exc.read(1000001)
            if len(body) > 1000000:
                raise ValueError('Oversized robots error response')
            lines = body.decode('utf-8', 'replace').splitlines()
            parser.parse(lines if any(line.strip().lower().startswith('user-agent:') for line in lines) else [])
            event(stage='robots', url=robots_url, result='absent_or_error_body_rules', status=exc.code)
            exc.close()
        except Exception as exc:
            event(stage='robots', url=robots_url, result='unreachable', error=str(exc)[:300])
            raise
        self.robots[host] = parser
    parser = self.robots[host]
    if not parser.can_fetch('CheyenneLaramieArchive', url):
        event(stage='policy', url=url, result='robots_denied')
        raise ValueError('Explicit robots disallow')
    delay = parser.crawl_delay('CheyenneLaramieArchive') or parser.crawl_delay('*') or 2
    time.sleep(max(0, delay - (time.monotonic() - self.last)))
    try:
        data = self.raw(url)
        event(stage='record', url=url, result='downloaded', bytes=len(data))
        return data
    except Exception as exc:
        event(stage='record', url=url, result='failed', error=str(exc)[:300])
        raise

def main():
    config = json.loads(Path('external-sources.json').read_text())
    path = Path('external-state.json')
    if path.exists():
        state = json.loads(path.read_text())
        queued = {x[0] for x in state['queue']}
        retry = [u for u in config['seeds'] if urlsplit(u).hostname in {'laramiecounty.legistar.com', 'gov.arcasearch.com', 'maps.laramiecounty.com'}]
        state['seen'] = [u for u in state['seen'] if u not in retry]
        state['queue'] = [[u, None] for u in retry if u not in queued] + state['queue']
        path.write_text(json.dumps(state, indent=2))
    adapters.Fetcher.get = compliant_get
    external.main()

if __name__ == '__main__':
    main()
