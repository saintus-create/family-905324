#!/usr/bin/env python3
"""Refresh California Judicial Council Invitations to Comment.

The script indexes the Judicial Branch's active-proposals page, downloads each
official proposal PDF, extracts its complete text into an accessible Fern page,
and writes a provenance-preserving JSON feed. It never submits comments.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from pypdf import PdfReader

SOURCE_URL = "https://courts.ca.gov/policy-administration/invitations-comment"
ARCHIVE_URL = "https://courts.ca.gov/policy-administration/invitations-comment/archived-past-proposals"
ABOUT_URL = "https://courts.ca.gov/policy-administration/invitations-comment/about-invitations-comment-itcs"
DEFAULT_DATA_PATH = Path("fern/data/judicial/invitations-to-comment.json")
DEFAULT_PAGE_PATH = Path("fern/docs/pages/invitations-to-comment.mdx")
DEFAULT_DETAIL_DIR = Path("fern/docs/pages/invitations-to-comment")
DEFAULT_ASSET_DIR = Path("fern/docs/assets/invitations-to-comment")
USER_AGENT = "California-family-law-research/1.0 (+public-proposal-index)"


def clean_text(value: str) -> str:
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def first(pattern: str, value: str, *, flags: int = re.I | re.S) -> str:
    match = re.search(pattern, value, flags)
    return clean_text(match.group(1)) if match else ""


def first_href(pattern: str, value: str) -> str:
    match = re.search(pattern, value, re.I | re.S)
    return html.unescape(match.group(1)).strip() if match else ""


def parse_deadline(value: str) -> str:
    if not value:
        return ""
    for pattern in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value, pattern).date().isoformat()
        except ValueError:
            pass
    return ""


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def fetch_url(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def fetch_source() -> str:
    return fetch_url(SOURCE_URL).decode("utf-8", "replace")


def parse_proposals(source: str) -> list[dict[str, str]]:
    blocks = re.findall(
        r'<div class="result-excerpt switcher result-excerpt--default">(.*?)</li>',
        source,
        flags=re.I | re.S,
    )
    proposals: list[dict[str, str]] = []
    seen: set[str] = set()

    for block in blocks:
        category = first(r'result-excerpt__brow-primary">(.*?)</span>', block)
        proposal_id = first(r'result-excerpt__brow-secondary">(.*?)</span>', block)
        deadline_label = first(r'result-excerpt__brow-notation">\s*Deadline:\s*(.*?)</div>', block)
        title = first(r'result-excerpt__heading">\s*<div>(.*?)</div>', block)
        pdf_url = first_href(r'<a href="([^"]+)"[^>]*>\s*Download PDF', block)
        comment_url = first_href(r'<a href="([^"]*itc-webform[^"]*)"', block)
        summary = first(r'result-excerpt__content.*?<div><p>(.*?)</p>', block)

        if not proposal_id or proposal_id in seen or not title:
            continue
        seen.add(proposal_id)
        slug = slugify(proposal_id)
        proposals.append(
            {
                "id": proposal_id,
                "slug": slug,
                "category": category,
                "title": title,
                "deadline": parse_deadline(deadline_label),
                "deadline_label": deadline_label,
                "summary": summary,
                "pdf_url": urljoin(SOURCE_URL, pdf_url) if pdf_url else "",
                "comment_url": urljoin(SOURCE_URL, comment_url) if comment_url else "",
                "comment_email": "invitations@jud.ca.gov",
                "source_url": SOURCE_URL,
                "detail_path": f"/invitations-to-comment/{slug}",
                "status": "active",
            }
        )

    proposals.sort(key=lambda item: (item["deadline"] or "9999-12-31", item["id"]))
    return proposals


def extract_pdf(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = (page.extract_text() or "").replace("\x00", "").strip()
        pages.append(text)
    return pages


def render_detail_page(proposal: dict[str, str], pages: list[str], local_pdf: str, retrieved_at: str) -> str:
    title = proposal["title"].replace('"', "'")
    lines = [
        "---",
        f'title: "{proposal["id"]}: {title}"',
        f'subtitle: "Full text of the official invitation to comment"',
        f'slug: invitations-to-comment/{proposal["slug"]}',
        "---",
        "",
        "<Callout intent=\"warning\">",
        "This proposal has not been approved by the Judicial Council and is circulated for comment only. Comments submitted to the Judicial Council become part of the public record.",
        "</Callout>",
        "",
        f'**Category:** {proposal["category"]}  ',
        f'**Comment deadline:** {proposal["deadline_label"]}  ',
        f'**Official proposal:** [Open or download the PDF]({local_pdf})  ',
        f'**Submit comments:** [Online form]({proposal["comment_url"]}) · [Email](mailto:{proposal["comment_email"]})',
        "",
        proposal["summary"],
        "",
        "## Complete proposal text",
        "",
        "The text below is extracted from the official PDF for searching and accessibility. Formatting, underlining, strikeouts, diagrams, and pagination may not be reproduced exactly. Use the PDF above as the controlling copy.",
        "",
    ]

    for number, page_text in enumerate(pages, start=1):
        # A text fence preserves every extracted character while preventing MDX
        # from interpreting legal braces, angle brackets, or amendment marks.
        safe_text = page_text.replace("```", "` ` `")
        lines.extend([f"### PDF page {number}", "", "```text", safe_text, "```", ""])

    lines.extend(
        [
            "## Source record",
            "",
            f'- Proposal identifier: **{proposal["id"]}**',
            f'- Official source page: [California Courts]({proposal["source_url"]})',
            f'- Official remote PDF: [View at courts.ca.gov]({proposal["pdf_url"]})',
            f'- Retrieved: {retrieved_at}',
            "",
        ]
    )
    return "\n".join(lines)


def populate_full_text(
    proposals: list[dict[str, str]],
    detail_dir: Path,
    asset_dir: Path,
    retrieved_at: str,
) -> None:
    detail_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)

    for proposal in proposals:
        if not proposal["pdf_url"]:
            continue
        pdf_name = f'{proposal["slug"]}.pdf'
        pdf_path = asset_dir / pdf_name
        pdf_bytes = fetch_url(proposal["pdf_url"])
        pdf_path.write_bytes(pdf_bytes)
        pages = extract_pdf(pdf_path)
        local_pdf = f'/assets/invitations-to-comment/{pdf_name}'
        detail_path = detail_dir / f'{proposal["slug"]}.mdx'
        detail_path.write_text(render_detail_page(proposal, pages, local_pdf, retrieved_at))
        proposal["local_pdf"] = local_pdf
        proposal["page_count"] = len(pages)
        proposal["text_characters"] = sum(len(page) for page in pages)
        proposal["pdf_sha256"] = hashlib.sha256(pdf_bytes).hexdigest()


def timing_label(proposal: dict[str, str], today: date) -> str:
    deadline = date.fromisoformat(proposal["deadline"]) if proposal["deadline"] else None
    days = (deadline - today).days if deadline else None
    if days is None:
        return proposal["deadline_label"] or "See the official proposal"
    if days == 0:
        return f'{proposal["deadline_label"]} — due today'
    if days == 1:
        return f'{proposal["deadline_label"]} — 1 day remaining'
    if days > 1:
        return f'{proposal["deadline_label"]} — {days} days remaining'
    return f'{proposal["deadline_label"]} — deadline passed; verify status with the Judicial Council'


def render_page(proposals: list[dict[str, str]], retrieved_at: str) -> str:
    lines = [
        "---",
        "title: Invitations to Comment",
        "subtitle: Active Judicial Council proposals, complete text, and official comment links",
        "slug: invitations-to-comment",
        "---",
        "",
        "<Callout intent=\"warning\">",
        "Comments submitted to the Judicial Council become part of the public record. These proposals are circulated for comment only and have not been approved by the Judicial Council.",
        "</Callout>",
        "",
        "## Active proposals",
        "",
    ]

    if not proposals:
        lines.extend(
            [
                "No active proposals were listed when this page was updated.",
                "",
                f"[Check the official Invitations to Comment page]({SOURCE_URL}).",
                "",
            ]
        )
    else:
        today = date.fromisoformat(retrieved_at[:10])
        for proposal in proposals:
            lines.extend(
                [
                    f'### [{proposal["title"]}]({proposal["detail_path"]})',
                    "",
                    f'**{proposal["id"]}** · {proposal["category"]}',
                    "",
                    f'**Comment deadline:** {timing_label(proposal, today)}',
                    "",
                    proposal["summary"],
                    "",
                ]
            )
            links = [f'[Read the complete proposal]({proposal["detail_path"]})']
            if proposal.get("local_pdf"):
                links.append(f'[Download the official PDF]({proposal["local_pdf"]})')
            if proposal["comment_url"]:
                links.append(f'[Submit comments online]({proposal["comment_url"]})')
            links.append(f'[Comment by email](mailto:{proposal["comment_email"]})')
            lines.extend([" · ".join(links), "", "---", ""])

    lines.extend(
        [
            "## How the process works",
            "",
            "1. Read the complete proposal and identify the specific rules, forms, standards, or legislation affected.",
            "2. Confirm the deadline and submission instructions on the official Judicial Branch page.",
            "3. Submit comments online or by email. Remember that submitted comments become public records.",
            "4. After circulation closes, follow Judicial Council meeting materials to see whether and how the proposal changes.",
            "",
            "## Official resources",
            "",
            f'- [Current Invitations to Comment]({SOURCE_URL})',
            f'- [Previously circulated proposals]({ARCHIVE_URL})',
            f'- [About the invitation-to-comment process]({ABOUT_URL})',
            "- [Judicial Council meetings and materials](https://courts.ca.gov/policy-administration/judicial-council/judicial-council-meetings)",
            "",
            f'*Source checked: {retrieved_at}. Deadlines and proposal status should always be confirmed on the official Judicial Branch website.*',
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-file", type=Path, help="Parse saved HTML instead of fetching the source")
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--page-path", type=Path, default=DEFAULT_PAGE_PATH)
    parser.add_argument("--detail-dir", type=Path, default=DEFAULT_DETAIL_DIR)
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSET_DIR)
    parser.add_argument("--retrieved-at", help="Override retrieval time (ISO-8601), primarily for tests")
    args = parser.parse_args()

    source = args.source_file.read_text() if args.source_file else fetch_source()
    proposals = parse_proposals(source)
    if not proposals and "No active proposals" not in source:
        raise RuntimeError("No active proposals could be parsed; source markup may have changed")

    retrieved_at = args.retrieved_at or datetime.now(timezone.utc).isoformat()
    populate_full_text(proposals, args.detail_dir, args.asset_dir, retrieved_at)
    payload = {
        "version": "1.1",
        "retrieved_at": retrieved_at,
        "source": {
            "title": "Judicial Branch of California — Invitations to Comment",
            "url": SOURCE_URL,
        },
        "records": proposals,
    }

    args.data_path.parent.mkdir(parents=True, exist_ok=True)
    args.page_path.parent.mkdir(parents=True, exist_ok=True)
    args.data_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    args.page_path.write_text(render_page(proposals, retrieved_at))
    print(f"Wrote {len(proposals)} active proposal(s) with complete extracted text")


if __name__ == "__main__":
    main()
