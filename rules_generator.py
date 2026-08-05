#!/usr/bin/env python3
"""
Rules of Court page generator for Fern docs.

Reads RULES_OF_COURT.json and produces:
  - court-rules-overview.mdx   (overview with cards linking to each title)
  - title-1.mdx ... title-10.mdx  (one page per title, all rules inline)
  - abusive-personality.mdx    (placeholder so docs.yml has no broken links)

Mirrors the style and helpers of generate_family_code_docs.py.
"""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / 'RULES_OF_COURT.json'
PAGES_DIR = ROOT / 'fern' / 'docs' / 'pages'


# ---------------------------------------------------------------------------
# Shared helpers (kept in sync with generate_family_code_docs.py)
# ---------------------------------------------------------------------------

def sanitize_text(value: str) -> str:
    text = value or ''
    text = text.replace('\u00a0', ' ')
    text = text.replace('—', '-')
    text = text.replace('–', '-')
    text = text.replace('**', '')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+\.', '.', text)
    text = re.sub(r'\s+,', ',', text)
    text = re.sub(r'\s+\)', ')', text)
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s*\(Added by .*?\)\s*', ' ', text)
    text = re.sub(r'\s*\(Amended by .*?\)\s*', ' ', text)
    text = re.sub(r'\s*\(Enacted by .*?\)\s*', ' ', text)
    text = re.sub(r'\s*\(.*?\)_', '', text)
    text = text.replace('_( ', '').replace('_', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    value = value.strip('-')
    return value or 'page'


# ---------------------------------------------------------------------------
# Hierarchy helpers
# ---------------------------------------------------------------------------

def group_rules(rules: list) -> list:
    """
    Group rules into a hierarchical structure.

    Returns a list of divisions (or a single pseudo-division when no
    divisions exist), each containing chapters, each containing articles
    (or a single pseudo-article), each containing a list of rules.

    Structure:
        [
            {
                'name': 'Division 1. General Provisions' or None,
                'chapters': [
                    {
                        'name': 'Chapter 1. Preliminary Rules',
                        'articles': [
                            {
                                'name': 'Article 1. ...' or None,
                                'rules': [rule, rule, ...],
                            },
                        ],
                    },
                ],
            },
        ]
    """
    divisions = {}  # name -> chapters dict
    division_order = []

    for rule in rules:
        div_name = rule.get('division') or None
        ch_name = rule.get('chapter') or 'General'
        art_name = rule.get('article') or None

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
                article_list.append({
                    'name': art_name,
                    'rules': articles_dict[art_name],
                })
            chapter_list.append({
                'name': ch_name,
                'articles': article_list,
            })
        result.append({
            'name': div_name,
            'chapters': chapter_list,
        })
    return result


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------

def build_overview_page(titles: list) -> str:
    lines = [
        '---',
        'title: Court Rules Overview',
        'subtitle: California Rules of Court',
        'slug: court-rules-overview',
        '---',
        '',
        '# California Rules of Court',
        '',
        'The California Rules of Court are organized into ten titles covering '
        'rules applicable to all courts, trial court rules, civil rules, '
        'criminal rules, family and juvenile rules, probate and mental health '
        'rules, appellate rules, rules on law practice and attorneys, and '
        'judicial administration.',
        '',
    ]

    for title in titles:
        title_number = title.get('title_number', '')
        title_name = sanitize_text(title.get('title_name', ''))
        rules = title.get('rules', [])
        count = len(rules)
        slug = f'title-{title_number}'

        card_title = title_name or f'Title {title_number}'

        count_label = f'{count} rule{"s" if count != 1 else ""}'
        if count == 0:
            count_label = 'Reserved (no rules)'

        lines.append(
            f'<Card title="{card_title}" '
            f'icon="fa-regular fa-book" href="/{slug}">'
        )
        lines.append(f'  {count_label}')
        lines.append('</Card>')
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def build_rule_block(rule: dict, level: int = 3) -> list:
    """Return markdown lines for a single rule at the given heading level."""
    rule_number = sanitize_text(rule.get('rule_number', ''))
    rule_title = sanitize_text(rule.get('rule_title', ''))
    legal_text = sanitize_text(rule.get('legal_text', '') or rule.get('full_text', ''))
    history = sanitize_text(rule.get('history', '') or rule.get('history_effective_date', ''))

    header = rule_number
    if rule_title and rule_title.lower() not in ('title', ''):
        header = f'{rule_number} - {rule_title}'

    hashes = '#' * level
    lines = [f'{hashes} {header}', '']
    if legal_text:
        lines.append(legal_text)
        lines.append('')
    if history:
        lines.append(f'> {history}')
        lines.append('')
    return lines


def build_title_page(title: dict) -> str:
    title_number = title.get('title_number', '')
    title_name = sanitize_text(title.get('title_name', ''))
    rules = title.get('rules', [])
    slug = f'title-{title_number}'

    # Frontmatter
    page_title = title_name or f'Title {title_number}'
    count = len(rules)
    subtitle = f'{count} rule{"s" if count != 1 else ""}' if count else 'Reserved'

    lines = [
        '---',
        f'title: {page_title}',
        f'subtitle: {subtitle}',
        f'slug: {slug}',
        '---',
        '',
        f'# {page_title}',
        '',
    ]

    # Title 6 has no rules
    if not rules:
        lines.append('This title is currently reserved and contains no rules.')
        lines.append('')
        citation = title.get('title_number_citation', '')
        if citation:
            lines.append(f'Source: [{citation}]({citation})')
            lines.append('')
        return '\n'.join(lines).rstrip() + '\n'

    # Group rules hierarchically
    grouped = group_rules(rules)

    has_divisions = any(d['name'] is not None for d in grouped)
    ch_level = 3 if has_divisions else 2

    for div in grouped:
        div_name = div['name']

        if has_divisions and div_name:
            lines.append(f'## {sanitize_text(div_name)}')
            lines.append('')

        for chapter in div['chapters']:
            ch_name = sanitize_text(chapter['name'])
            lines.append(f'{"#" * ch_level} {ch_name}')
            lines.append('')

            has_articles = any(a['name'] is not None for a in chapter['articles'])
            rule_level = ch_level + 2 if has_articles else ch_level + 1

            for article in chapter['articles']:
                art_name = article['name']

                if has_articles and art_name:
                    lines.append(f'{"#" * (ch_level + 1)} {sanitize_text(art_name)}')
                    lines.append('')

                for rule in article['rules']:
                    lines.extend(build_rule_block(rule, level=rule_level))

    return '\n'.join(lines).rstrip() + '\n'


def build_abuse_page() -> str:
    lines = [
        '---',
        'title: The Abusive Personality',
        'subtitle: Legal Research Notes',
        'slug: abusive-personality',
        '---',
        '',
        '# The Abusive Personality',
        '',
        'Content for this page is forthcoming.',
        '',
    ]
    return '\n'.join(lines).rstrip() + '\n'


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_pages(titles: list):
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Overview
    overview = build_overview_page(titles)
    (PAGES_DIR / 'court-rules-overview.mdx').write_text(overview)

    # One page per title
    for title in titles:
        title_number = title.get('title_number', '')
        page = build_title_page(title)
        (PAGES_DIR / f'title-{title_number}.mdx').write_text(page)

    # Abuse placeholder
    (PAGES_DIR / 'abusive-personality.mdx').write_text(build_abuse_page())

    total_rules = sum(len(t.get('rules', [])) for t in titles)
    print(f'Generated {len(titles)} title pages + overview from {total_rules} rules.')


def main():
    data = json.loads(JSON_PATH.read_text())
    titles = data.get('titles', [])
    write_pages(titles)


if __name__ == '__main__':
    main()
