#!/usr/bin/env python3
"""Index literal Uber Base / Base Web source and documentation.

The pinned `vendor/baseweb` submodule is the complete upstream system. This
script never paraphrases its documentation: it creates a provenance index for
every documentation page, example, and implementation file used by Base Web.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'vendor'/'baseweb'
OUT=ROOT/'fern'/'data'/'design-systems'/'base-web'/'source-index.json'
INCLUDE=(BASE/'documentation-site'/'pages', BASE/'documentation-site'/'examples', BASE/'documentation-site'/'components', BASE/'src')
SUFFIXES={'.ts','.tsx','.js','.jsx','.md','.mdx','.json','.css'}
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def main():
 if not BASE.exists(): raise SystemExit('Base Web submodule is not initialized. Run git submodule update --init --recursive.')
 files=[]
 for root in INCLUDE:
  if not root.exists(): continue
  for p in sorted(root.rglob('*')):
   if p.is_file() and p.suffix in SUFFIXES:
    files.append({'path':str(p.relative_to(BASE)),'bytes':p.stat().st_size,'sha256':digest(p),'kind':'documentation' if 'documentation-site' in p.parts else 'implementation'})
 OUT.parent.mkdir(parents=True,exist_ok=True)
 payload={'system':'Uber Base / Base Web','upstream_repository':'https://github.com/uber/baseweb','upstream_commit':__import__('subprocess').check_output(['git','-C',str(BASE),'rev-parse','HEAD'],text=True).strip(),'created_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),'purpose':'Literal source index. All referenced contents remain in the pinned Base Web submodule; this manifest supports traceability and implementation mapping.','file_count':len(files),'files':files}
 OUT.write_text(json.dumps(payload,indent=2)+'\n')
 print(f'Indexed {len(files)} Base Web source and documentation files')
if __name__=='__main__':main()
