#!/usr/bin/env python3
"""
Rules of Court page generator for Fern docs (corrected version).

Fixes vs. the original rules_generator.py:
  - sanitize_text no longer collapses newlines before stripping citation
    parentheticals, which was deleting large spans of legitimate rule text
    (the non-greedy \\(.*?\\)_ regex was spanning from the first "(" in a
    rule all the way to a single distant ")_" near an italicized markdown
    link, silently deleting everything in between).
  - Rules are now sorted numerically within each chapter/article instead of
    left in source-file order (which was not numeric - e.g. Rule 1.2 before
    Rule 1.1).
  - No duplicate H1: the page title is already rendered by Fern from the
    frontmatter `title:` field, so the body no longer repeats it.
  - Heading level starts at H2 (not H1) to avoid skipping a level.
"""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "RULES_OF_COURT.json"
PAGES_DIR = ROOT / "fern" / "docs" / "pages"


def sanitize_text(value):
    text = value or ""
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2014", "-")
    text = text.replace("\u2013", "-")
    text = text.replace("**", "")

    text = re.sub(r"\s*\(Added by [^)]*?\)\s*", " ", text)
    text = re.sub(r"\s*\(Amended by [^)]*?\)\s*", " ", text)
    text = re.sub(r"\s*\(Enacted by [^)]*?\)\s*", " ", text)

    paragraphs = re.split(r"\n\s*\n", text)
    cleaned_paragraphs = []
    for p in paragraphs:
        p = re.sub(r"\s+", " ", p).strip()
        p = re.sub(r"\s+\.", ".", p)
        p = re.sub(r"\s+,", ",", p)
        p = re.sub(r"\s+\)", ")", p)
        p = re.sub(r"\(\s+", "(", p)
        if p:
            cleaned_paragraphs.append(p)

    return "\n\n".join(cleaned_paragraphs)


def slugify(value):
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "page"


def rule_sort_key(rule):
    num = rule.get("rule_number", "")
    m = re.search(r"(\d+)(?:\.(\d+))?", num)
    if not m:
        return (float("inf"), float("inf"))
    major = int(m.group(1))
    minor = int(m.group(2)) if m.group(2) else 0
    return (major, minor)


def group_rules(rules):
    divisions = {}
    division_order = []

    for rule in rules:
        div_name = rule.get("division") or None
        ch_name = rule.get("chapter") or "General"
        art_name = rule.get("article") or None

        if div_name not in divisions:
            divisions[div_name] = {}
            division_order.append(div_name)
        chapters = divisions[div_name]

        if ch_name not in chapters:
            chapters[ch_name] = {}
        articles = chapters[ch_name]

        if art_name not in articles:
            articles[art_name] = []
        articles[art_name].append(rule)

    result = []
    for div_name in division_order:
        chapters_dict = divisions[div_name]
        chapter_list = []
        for ch_name in chapters_dict:
            articles_dict = chapters_dict[ch_name]
            article_list = []
            for art_name in articles_dict:
                rules_sorted = sorted(articles_dict[art_name], key=rule_sort_key)
                article_list.append({"name": art_name, "rules": rules_sorted})
            chapter_list.append({"name": ch_name, "articles": article_list})
        result.append({"name": div_name, "chapters": chapter_list})
    return result


def build_overview_page(titles):
    lines = [
        "---",
        "title: Court Rules Overview",
        "subtitle: California Rules of Court",
        "slug: court-rules-overview",
        "---",
        "",
        "The California Rules of Court are organized into ten titles covering "
        "rules applicable to all courts, trial court rules, civil rules, "
        "criminal rules, family and juvenile rules, probate and mental health "
        "rules, appellate rules, rules on law practice and attorneys, and "
        "judicial administration.",
        "",
    ]

    for title in titles:
        title_number = title.get("title_number", "")
        title_name = sanitize_text(title.get("title_name", ""))
        rules = title.get("rules", [])
        count = len(rules)
        slug = f"title-{title_number}"
        card_title = title_name or f"Title {title_number}"
        count_label = f'{count} rule{"s" if count != 1 else ""}'
        if count == 0:
            count_label = "Reserved (no rules)"
        lines.append(f'<Card title="{card_title}" icon="fa-regular fa-book" href="/{slug}">')
        lines.append(f"  {count_label}")
        lines.append("</Card>")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_rule_block(rule, level=3):
    rule_number = sanitize_text(rule.get("rule_number", ""))
    rule_title = sanitize_text(rule.get("rule_title", ""))
    legal_text = sanitize_text(rule.get("legal_text", "") or rule.get("full_text", ""))
    history = sanitize_text(rule.get("history", "") or rule.get("history_effective_date", ""))

    header = rule_number
    if rule_title:
        header = f"{rule_number}: {rule_title}"

    hashes = "#" * level
    lines = [f"{hashes} {header}", ""]
    if legal_text:
        lines.append(legal_text)
        lines.append("")
    if history:
        lines.append(f"> {history}")
        lines.append("")
    return lines


def build_title_page(title):
    title_number = title.get("title_number", "")
    title_name = sanitize_text(title.get("title_name", ""))
    rules = title.get("rules", [])
    slug = f"title-{title_number}"

    page_title = title_name or f"Title {title_number}"
    count = len(rules)
    subtitle = f'{count} rule{"s" if count != 1 else ""}' if count else "Reserved"

    lines = ["---", f"title: {page_title}", f"subtitle: {subtitle}", f"slug: {slug}", "---", ""]

    if not rules:
        lines.append("This title is currently reserved and contains no rules.")
        lines.append("")
        citation = title.get("title_number_citation", "")
        if citation:
            lines.append(f"Source: [{citation}]({citation})")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    grouped = group_rules(rules)
    has_divisions = any(d["name"] is not None for d in grouped)
    ch_level = 3 if has_divisions else 2

    for div in grouped:
        div_name = div["name"]
        if has_divisions and div_name:
            lines.append(f"## {sanitize_text(div_name)}")
            lines.append("")

        for chapter in div["chapters"]:
            ch_name = sanitize_text(chapter["name"])
            lines.append(f'{"#" * ch_level} {ch_name}')
            lines.append("")

            has_articles = any(a["name"] is not None for a in chapter["articles"])
            rule_level = ch_level + 2 if has_articles else ch_level + 1

            for article in chapter["articles"]:
                art_name = article["name"]
                if has_articles and art_name:
                    lines.append(f'{"#" * (ch_level + 1)} {sanitize_text(art_name)}')
                    lines.append("")

                for rule in article["rules"]:
                    lines.extend(build_rule_block(rule, level=rule_level))

    return "\n".join(lines).rstrip() + "\n"


def write_pages(titles):
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    overview = build_overview_page(titles)
    (PAGES_DIR / "court-rules-overview.mdx").write_text(overview)

    for title in titles:
        title_number = title.get("title_number", "")
        page = build_title_page(title)
        (PAGES_DIR / f"title-{title_number}.mdx").write_text(page)

    total_rules = sum(len(t.get("rules", [])) for t in titles)
    print(f"Generated {len(titles)} title pages + overview from {total_rules} rules.")


def main():
    data = json.loads(JSON_PATH.read_text())
    titles = data.get("titles", [])
    write_pages(titles)


if __name__ == "__main__":
    main()
