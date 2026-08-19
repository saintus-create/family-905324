#!/usr/bin/env python3
"""Build a searchable catalog of California measures from official bill data."""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

SESSION = "2025-2026"
SESSION_ID = "20252026"
SOURCE_URL = f"https://leginfo.legislature.ca.gov/faces/billSearchClient.xhtml?session_year={SESSION_ID}"
OUTPUT_PATH = Path(f"fern/docs/assets/legislation/california-measures-{SESSION_ID}.json")
USER_AGENT = "California-family-law-research/1.0 (+public-legislation-index)"

FAMILY_TERMS = (
    "adoption", "child", "children", "custody", "dependent", "dependency",
    "divorce", "domestic violence", "family", "foster", "guardian", "juvenile",
    "marriage", "minor", "parent", "parentage", "protective order", "restraining order",
    "spousal", "support", "visitation",
)

MEASURE_TYPES = {
    "AB": ("Assembly", "Assembly bill"),
    "ACA": ("Assembly", "Assembly constitutional amendment"),
    "ACR": ("Assembly", "Assembly concurrent resolution"),
    "AJR": ("Assembly", "Assembly joint resolution"),
    "AR": ("Assembly", "Assembly resolution"),
    "HR": ("Assembly", "Assembly house resolution"),
    "GRP": ("Executive", "Governor's reorganization plan"),
    "SB": ("Senate", "Senate bill"),
    "SCA": ("Senate", "Senate constitutional amendment"),
    "SCR": ("Senate", "Senate concurrent resolution"),
    "SJR": ("Senate", "Senate joint resolution"),
    "SR": ("Senate", "Senate resolution"),
}


def fetch_source() -> str:
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read().decode("utf-8", "replace")


def clean(value: str) -> str:
    value = re.sub(r"<!--.*?-->", " ", value, flags=re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def author_directory(source: str) -> dict[str, str]:
    select = re.search(r'<select id="author".*?</select>', source, flags=re.I | re.S)
    if not select:
        return {}
    directory = {}
    for value, label in re.findall(r'<option value="([^"]+)"[^>]*>(.*?)</option>', select.group(0), flags=re.I | re.S):
        key = clean(value)
        display = clean(label)
        if key == "All" or not key:
            continue
        if "," in display:
            last, first = [part.strip() for part in display.split(",", 1)]
            display = f"{first} {last}".strip()
        directory[key] = display
    return directory


def measure_classification(measure: str) -> tuple[str, str, bool]:
    prefix_match = re.match(r"([A-Z]+)", measure)
    prefix = prefix_match.group(1) if prefix_match else ""
    # Special-session measures include X plus the session number in the display
    # (for example, ABX1-1) while retaining their Assembly/Senate type.
    normalized_prefix = re.sub(r"X\d*$", "", prefix)
    chamber, measure_type = MEASURE_TYPES.get(normalized_prefix, ("Other", "Other measure"))
    return chamber, measure_type, "X" in prefix


def status_group(status: str) -> str:
    lowered = status.lower()
    if "chaptered" in lowered:
        return "Chaptered"
    if "vetoed" in lowered:
        return "Vetoed"
    if any(term in lowered for term in ("died", "failed", "inactive", "withdrawn")):
        return "Inactive"
    if "enrolled" in lowered:
        return "Enrolled"
    return "Active"


def parse_records(source: str) -> list[dict]:
    directory = author_directory(source)
    rows = re.findall(
        r'<tr>\s*<td><a href="([^"]*bill_id=([^"]+))">(.*?)</a></td>'
        r'\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>',
        source,
        flags=re.I | re.S,
    )
    records = []
    for href, bill_id, measure_html, subject_html, author_html, status_html in rows:
        measure = clean(measure_html)
        subject = clean(subject_html)
        author_key = clean(author_html)
        status = clean(status_html)
        if not measure or not bill_id:
            continue
        chamber, measure_type, special_session = measure_classification(measure)
        author = directory.get(author_key, author_key or "Not listed")
        haystack = f"{subject} {measure_type}".lower()
        family_terms = [term for term in FAMILY_TERMS if term in haystack]
        records.append(
            {
                "bill_id": bill_id,
                "measure": measure.replace("-", " ", 1),
                "measure_display": measure,
                "measure_type": measure_type,
                "chamber": chamber,
                "special_session": special_session,
                "subject": subject,
                "author": author,
                "author_key": author_key,
                "status": status,
                "status_group": status_group(status),
                "family_law_relevance": bool(family_terms),
                "family_law_terms": family_terms,
                "official_url": urljoin(SOURCE_URL, href),
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-file", type=Path, help="Parse saved HTML rather than fetching the official page")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--retrieved-at", help="Override retrieval time for deterministic tests")
    parser.add_argument("--force", action="store_true", help="Rewrite output even when records are unchanged")
    args = parser.parse_args()

    source = args.source_file.read_text() if args.source_file else fetch_source()
    records = parse_records(source)
    if len(records) < 1000:
        raise RuntimeError(f"Parsed only {len(records)} measures; official source markup may have changed")

    if args.output.exists() and not args.force:
        try:
            previous = json.loads(args.output.read_text())
            if previous.get("records") == records:
                print(f"Catalog unchanged at {len(records)} measures")
                return
        except (OSError, json.JSONDecodeError):
            pass

    counts = {
        "total": len(records),
        "assembly": sum(record["chamber"] == "Assembly" for record in records),
        "senate": sum(record["chamber"] == "Senate" for record in records),
        "family_law_matches": sum(record["family_law_relevance"] for record in records),
    }
    payload = {
        "version": "1.0",
        "session": SESSION,
        "session_id": SESSION_ID,
        "retrieved_at": args.retrieved_at or datetime.now(timezone.utc).isoformat(),
        "source": {
            "title": "California Legislative Information — Bill Search",
            "url": SOURCE_URL,
            "publisher": "California Office of Legislative Counsel",
        },
        "counts": counts,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Wrote {len(records)} California measures for the {SESSION} session")


if __name__ == "__main__":
    main()
