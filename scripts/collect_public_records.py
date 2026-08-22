#!/usr/bin/env python3
"""Collect narrowly scoped, public, traceable research snapshots.

Only registry URLs and explicit USAspending query payloads are fetched. The
script records retrieval metadata and raw source responses; it never scrapes
restricted material or attempts to identify private persons.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "fern" / "data" / "public-records"
REGISTRY = DATA / "source-registry.json"
SNAPSHOTS = DATA / "snapshots"
USER_AGENT = "FamilyLawPublicRecordsResearch/1.0 (public-source preservation)"

def utcnow(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def digest(b): return hashlib.sha256(b).hexdigest()
def fetch(url, method="GET", payload=None):
    headers={"User-Agent": USER_AGENT, "Accept": "application/json, text/html;q=0.9, */*;q=0.1"}
    if payload is not None: headers["Content-Type"]="application/json"
    req=Request(url, data=payload, headers=headers, method=method)
    with urlopen(req, timeout=45) as response:
        return response.status, response.headers.get_content_type(), response.read()
def write_snapshot(snapshot_id, source, body, content_type, request=None):
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    extension = ".json" if "json" in content_type else ".html"
    raw = SNAPSHOTS / f"{snapshot_id}{extension}"
    raw.write_bytes(body)
    meta={"snapshot_id":snapshot_id,"source_id":source["source_id"],"publisher":source["publisher"],"url":source["url"],"retrieved_at":utcnow(),"content_type":content_type,"bytes":len(body),"sha256":digest(body),"request":request,"scope_note":"Raw public-source snapshot. Presence is not a finding and does not establish a relationship, award, payment, or allegation."}
    (SNAPSHOTS / f"{snapshot_id}.metadata.json").write_text(json.dumps(meta,indent=2)+"\n")
    return meta
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--sources", action="store_true", help="snapshot approved public registry landing sources")
    parser.add_argument("--usaspending-santa-barbara", action="store_true", help="retrieve a reproducible federal-award discovery result for Santa Barbara County")
    args=parser.parse_args()
    if not (args.sources or args.usaspending_santa_barbara): parser.error("select at least one collection option")
    manifest=[]
    if args.sources:
        for source in json.loads(REGISTRY.read_text())["sources"]:
            try:
                status, ct, body=fetch(source["url"])
                if status != 200: raise RuntimeError(f"HTTP {status}")
                manifest.append(write_snapshot(f"{source['source_id']}-landing", source, body, ct))
            except Exception as exc:
                manifest.append({"source_id":source["source_id"],"url":source["url"],"retrieved_at":utcnow(),"collection_error":str(exc)})
    if args.usaspending_santa_barbara:
        source={"source_id":"usaspending_santa_barbara_grant_discovery","publisher":"U.S. Department of the Treasury","url":"https://api.usaspending.gov/api/v2/search/spending_by_award/"}
        payload={"filters":{"time_period":[{"start_date":"2020-01-01","end_date":"2026-08-22"}],"place_of_performance_locations":[{"country":"USA","state":"CA","county":"083"}],"award_type_codes":["02","03","04","05"]},"fields":["Award ID","Recipient Name","Awarding Agency","Award Amount","Description","Start Date","End Date","Place of Performance City Code","Place of Performance State Code"],"page":1,"limit":100,"sort":"Award Amount","order":"desc","subawards":False}
        status, ct, body=fetch(source["url"], "POST", json.dumps(payload).encode())
        if status != 200: raise RuntimeError(f"USAspending HTTP {status}")
        manifest.append(write_snapshot("usaspending-santa-barbara-grants-2020-2026", source, body, ct, request={"method":"POST","payload":payload}))
    (SNAPSHOTS / "collection-manifest.json").write_text(json.dumps({"schema_version":"1.0","updated_at":utcnow(),"entries":manifest},indent=2)+"\n")
    print(f"Wrote {len(manifest)} snapshot metadata records to {SNAPSHOTS}")
if __name__ == '__main__':
    try: main()
    except Exception as exc: print(f"collection failed: {exc}", file=sys.stderr); raise SystemExit(1)
