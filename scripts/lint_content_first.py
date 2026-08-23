#!/usr/bin/env python3
"""Reject AI process narration in visitor-facing MDX pages.

This is deliberately narrow: it flags product-planning prose, not legal source
text. A flagged page must be replaced with records, links, or sourced content.
"""
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
patterns=[
 r'\blong-term goal\b', r'\bfuture (?:research|record|analysis|interface|module|system)',
 r'\bthis project is designed\b', r'\bthe site is being built\b',
 r'\bthe system should\b', r'\bthe objective is\b', r'\bwill become useful\b',
 r'\beventual(?:ly)?\b'
]
failed=[]
for page in sorted((ROOT/'fern/docs/pages').rglob('*.mdx')):
    text=page.read_text(errors='ignore')
    for number,line in enumerate(text.splitlines(),1):
        if any(re.search(pattern,line,re.I) for pattern in patterns):
            failed.append(f'{page.relative_to(ROOT)}:{number}: {line.strip()}')
if failed:
    print('\n'.join(failed),file=sys.stderr); raise SystemExit(1)
print('Content-first lint passed.')
