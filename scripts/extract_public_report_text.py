#!/usr/bin/env python3
"""Produce searchable text companions for public PDF source snapshots.

The PDF stays the controlling artifact. Text is an extraction aid and is linked
back to the PDF hash in a companion metadata record.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
SNAPSHOTS=ROOT/'fern/data/public-records/snapshots'
def sha(b): return hashlib.sha256(b).hexdigest()
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
for pdf in sorted(SNAPSHOTS.glob('*.pdf')):
    try:
        reader=PdfReader(str(pdf))
        text='\n\n'.join(f'\n--- PAGE {i+1} ---\n{page.extract_text() or ""}' for i,page in enumerate(reader.pages))
        output=pdf.with_suffix('.extracted.txt'); output.write_text(text)
        metadata={'source_pdf':pdf.name,'source_pdf_sha256':sha(pdf.read_bytes()),'extracted_text':output.name,'extracted_text_sha256':sha(output.read_bytes()),'page_count':len(reader.pages),'extracted_at':now(),'notice':'Search aid only. Cite and interpret the controlling PDF page, not this extraction alone.'}
        pdf.with_suffix('.extracted.metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
        print(f'{pdf.name}: {len(reader.pages)} pages, {len(text)} characters')
    except Exception as exc:
        print(f'{pdf.name}: extraction unavailable: {exc}')
