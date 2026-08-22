#!/usr/bin/env python3
"""Collect published CJP public-decision index pages and retain local entries.

Only final/public decisions already published by the Commission are indexed.
"""
from __future__ import annotations
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import hashlib, json, time
from pathlib import Path
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'fern/data/public-records'; OUT=DATA/'public-officials'
BASE='https://cjp.ca.gov/discipline-decisions-database-results/?wpv_view_count=106760&wpv_paged={}'
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def get(url):
 with urlopen(Request(url,headers={'User-Agent':'FamilyLawPublicRecordsResearch/1.0'}),timeout=40) as r:return r.read()
def main():
 all_rows=[]; pages=[]
 for page in range(1,28):
  url=BASE.format(page); raw=get(url); pages.append({'page':page,'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
  soup=BeautifulSoup(raw,'html.parser'); table=soup.find('table')
  if not table: raise RuntimeError(f'No table on page {page}')
  for tr in table.find_all('tr')[1:]:
   cells=tr.find_all('td')
   if len(cells)!=10: continue
   link=cells[0].find('a')
   values=[c.get_text(' ',strip=True) for c in cells]
   all_rows.append({'last_name':values[0],'first_name':values[1],'inquiry_number':values[2] or None,'court_level':values[3],'county_or_district':values[4],'method_of_resolution':values[5],'decision_by':values[6],'discipline_or_determination':values[7],'date_of_decision':values[8],'petition_for_review':values[9] or None,'decision_url':link.get('href') if link else None,'index_page':page})
  time.sleep(.25)
 local=[r for r in all_rows if r['county_or_district'] in {'Santa Barbara','Ventura'}]
 result={'schema_version':'1.0','dataset_id':'cjp-public-decisions-santa-barbara-ventura','retrieved_at':now(),'publisher':'California Commission on Judicial Performance','index_url':'https://cjp.ca.gov/discipline-decisions-database-results/','scope':'Published CJP public-decision index entries whose county/appellate-district field is Santa Barbara or Ventura. This is not a complete judicial history, complaint log, or performance rating.','all_index_rows_observed':len(all_rows),'local_record_count':len(local),'source_pages':pages,'records':local}
 OUT.mkdir(exist_ok=True); (OUT/'cjp-public-decisions-santa-barbara-ventura.json').write_text(json.dumps(result,indent=2)+'\n')
 print(f'Indexed {len(all_rows)} published rows; retained {len(local)} Santa Barbara/Ventura entries')
if __name__=='__main__':main()
