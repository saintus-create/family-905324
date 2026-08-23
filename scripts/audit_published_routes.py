#!/usr/bin/env python3
"""Check that authored internal Fern links resolve on the published docs site."""
from __future__ import annotations
import re, sys
from pathlib import Path
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]
BASE='https://california-state-603082.docs.buildwithfern.com'
paths=sorted(set(re.findall(r'href="(/[^"]+)"', (ROOT/'fern/docs/pages/welcome.mdx').read_text())))
failed=[]
for path in paths:
    try:
        with urlopen(Request(BASE+path,headers={'User-Agent':'RouteAudit/1.0'}),timeout=30) as response:
            body=response.read().decode('utf-8','ignore')
            if "Sorry, we couldn't find that page" in body: failed.append(path)
            else: print('OK ',path)
    except Exception as exc:
        failed.append(f'{path} ({exc})')
if failed:
    print('FAILED:', *failed, sep='\n  ', file=sys.stderr); raise SystemExit(1)
