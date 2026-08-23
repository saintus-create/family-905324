#!/usr/bin/env python3
"""Synchronize the public Base Web documentation corpus with provenance.

This collector stores the literal public documentation pages used to govern the
local Base adoption. It is intentionally a source mirror, not a paraphrase.
Run with --sync to fetch pages; default mode only prints the current manifest.
"""
from __future__ import annotations
import argparse, hashlib, json, re, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'fern' / 'data' / 'design-systems' / 'base-web'
ORIGIN = 'https://baseweb.design/'
PREFIXES = ('components/', 'guides/', 'getting-started/', 'blog/')
USER_AGENT = 'CaliforniaFamilyLawResearch-BaseWebSourceSync/1.0'

def stamp(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def sha(data: bytes): return hashlib.sha256(data).hexdigest()
def allowed(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == 'https' and parsed.netloc == 'baseweb.design' and parsed.path.lstrip('/').startswith(PREFIXES)
def slug(url: str) -> str:
    path = urlparse(url).path.strip('/') or 'index'
    return re.sub(r'[^a-zA-Z0-9._-]+', '--', path) + '.html'
def fetch(url: str) -> bytes:
    request = Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'text/html,application/xhtml+xml'})
    with urlopen(request, timeout=45) as response:
        return response.read()
def text_from_html(data: bytes) -> str:
    soup = BeautifulSoup(data, 'html.parser')
    node = soup.select_one('main') or soup.select_one('#docSearch-content') or soup.body
    for unwanted in node.select('script, style, nav, footer, noscript'):
        unwanted.decompose()
    return node.get_text('\n', strip=True) + '\n'
def links_from_html(base: str, data: bytes) -> set[str]:
    soup = BeautifulSoup(data, 'html.parser')
    links=set()
    for tag in soup.select('a[href]'):
        url = urldefrag(urljoin(base, tag['href']))[0]
        if allowed(url): links.add(url)
    return links

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--sync', action='store_true')
    parser.add_argument('--max-pages', type=int, default=250)
    parser.add_argument('--delay', type=float, default=.25)
    args=parser.parse_args()
    manifest_path=OUT/'manifest.json'
    if not args.sync:
        print(manifest_path.read_text() if manifest_path.exists() else 'No Base Web corpus synced yet.')
        return
    OUT.mkdir(parents=True, exist_ok=True)
    queue=[urljoin(ORIGIN, p) for p in ('components/', 'guides/theming/', 'guides/colors/', 'getting-started/setup/', 'blog/')]
    seen=set(); entries=[]
    while queue and len(seen) < args.max_pages:
        url=queue.pop(0)
        if url in seen: continue
        seen.add(url)
        try:
            body=fetch(url)
            html_path=OUT/'pages'/slug(url); html_path.parent.mkdir(parents=True, exist_ok=True); html_path.write_bytes(body)
            text_path=html_path.with_suffix('.txt'); text_path.write_text(text_from_html(body))
            entries.append({'url':url, 'html':str(html_path.relative_to(OUT)), 'text':str(text_path.relative_to(OUT)), 'retrieved_at':stamp(), 'sha256':sha(body), 'bytes':len(body)})
            for link in sorted(links_from_html(url, body)):
                if link not in seen and link not in queue: queue.append(link)
            time.sleep(args.delay)
        except Exception as exc:
            entries.append({'url':url, 'retrieved_at':stamp(), 'error':str(exc)})
    manifest={'system':'Base Web','publisher':'Uber','origin':ORIGIN,'retrieved_at':stamp(),'purpose':'Literal public Base Web documentation corpus used as the implementation source for this repository. HTML is the preserved source; text files are search companions.','page_count':sum('html' in e for e in entries),'entries':entries}
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Synced {manifest["page_count"]} Base Web documentation pages to {OUT}')
if __name__ == '__main__': main()
