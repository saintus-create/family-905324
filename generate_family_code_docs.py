#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / 'tableofcontents.json'
DOCS_YML_PATH = ROOT / 'fern' / 'docs.yml'
PAGES_DIR = ROOT / 'fern' / 'docs' / 'pages'


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
    text = text.replace('FAMFamily Code - FAM', '')
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


def parse_range(value: str) -> str:
    if not value:
        return ''
    value = value.replace('\\[', '[').replace('\\]', ']')
    value = value.replace('[', '').replace(']', '')
    value = value.replace('**', '')
    return value.strip()


def build_division_page(division: dict) -> str:
    division_number = division.get('division_number', 'Division')
    division_title = sanitize_text(division.get('division_title', '').replace(division_number, '').strip())
    division_range = parse_range(division.get('division_title', ''))
    lines = [
        '---',
        f'title: {division_number}',
        f'subtitle: {division_title}',
        f'slug: {slugify(division_number)}',
        '---',
        '',
        f'## {division_number}',
        '',
        f'Title: {division_title}',
        f'Range: {division_range}',
        '',
    ]
    for part in division.get('parts', []):
        part_number = part.get('part_number', 'Part')
        part_title = sanitize_text(part.get('part_title', '').replace(part_number, '').strip())
        part_range = parse_range(part.get('part_title', ''))
        lines.extend([
            f'## {part_number}',
            '',
            f'Title: {part_title}',
            f'Range: {part_range}',
            '',
        ])
    return '\n'.join(lines).rstrip() + '\n'


def build_part_page(division: dict, part: dict) -> str:
    division_number = division.get('division_number', 'Division')
    part_number = part.get('part_number', 'Part')
    part_title = sanitize_text(part.get('part_title', '').replace(part_number, '').strip())
    part_range = parse_range(part.get('part_title', ''))
    lines = [
        '---',
        f'title: {division_number} {part_number}',
        f'subtitle: {part_title}',
        f'slug: {slugify(f"{division_number} {part_number}")}',
        '---',
        '',
        f'## {division_number}',
        '',
        f'Title: {sanitize_text(division.get("division_title", "").replace(division_number, "").strip())}',
        f'Range: {parse_range(division.get("division_title", ""))}',
        '',
        f'## {part_number}',
        '',
        f'Title: {part_title}',
        f'Range: {part_range}',
        '',
    ]
    for chapter in part.get('chapters', []):
        chapter_number = chapter.get('chapter_number', 'Chapter')
        chapter_title = sanitize_text(chapter.get('chapter_title', '').replace(chapter_number, '').strip())
        chapter_range = parse_range(chapter.get('chapter_title', ''))
        lines.extend([
            f'### {chapter_number}',
            '',
            f'Title: {chapter_title}',
            f'Range: {chapter_range}',
            '',
        ])
        for section in chapter.get('sections', []):
            section_number = section.get('section_number', 'Section')
            lines.append(f'#### {section_number}')
            lines.append('')
            for subsection in section.get('subsections', []):
                value = sanitize_text(subsection.get('value', ''))
                if value:
                    lines.append(value)
                    lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def build_overview_page() -> str:
    return '''---
title: Family Code Overview
subtitle: California Family Code
slug: family-code-overview
---

## Family Code Overview

'''


def write_pages(structure):
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    overview = build_overview_page()
    (PAGES_DIR / 'family-code-overview.mdx').write_text(overview)
    generated = []
    for division in structure:
        division_number = division.get('division_number', 'Division')
        division_slug = slugify(division_number)
        division_path = PAGES_DIR / f'{division_slug}.mdx'
        division_page = build_division_page(division)
        division_path.write_text(division_page)
        generated.append({
            'type': 'page',
            'label': f'{division_number}',
            'path': f'docs/pages/{division_slug}.mdx',
        })
        for part in division.get('parts', []):
            part_number = part.get('part_number', 'Part')
            part_label = f'{division_number} {part_number}'
            part_slug = slugify(part_label)
            part_path = PAGES_DIR / f'{part_slug}.mdx'
            part_path.write_text(build_part_page(division, part))
            generated.append({
                'type': 'page',
                'label': part_label,
                'path': f'docs/pages/{part_slug}.mdx',
            })
    return generated


def build_docs_yaml(generated):
    lines = [
        '# yaml-language-server: $schema=https://schema.buildwithfern.dev/docs-yml.json',
        '',
        'instances:',
        '  - url: california-state-603082.docs.buildwithfern.com',
        '    edit-this-page:',
        '      github:',
        '        owner: fern-starter',
        '        repo: family-905324',
        '        branch: main',
        '      launch: dashboard',
        'title: California Family Code | Legal Research',
        'layout:',
        '  searchbar-placement: header',
        '  page-width: full',
        '  tabs-placement: header',
        'tabs:',
        '  home:',
        '    display-name: Home',
        '    icon: home',
        '  family-code:',
        '    display-name: Family Code',
        '    icon: scale',
        '  changelog:',
        '    display-name: Changelog',
        '    icon: clock',
        'navigation:',
        '  - tab: home',
        '    layout:',
        '      - page: Home',
        '        path: docs/pages/welcome.mdx',
        '        slug: welcome',
        '  - tab: family-code',
        '    layout:',
        '      - page: Family Code Overview',
        '        path: docs/pages/family-code-overview.mdx',
        '        icon: fa-regular fa-scale-balanced',
    ]
    for item in generated:
        if item['label'] == 'Division 1':
            pass
    for top in generated:
        label = top['label']
        if label.startswith('Division '):
            lines.append('      - section: ' + label)
            lines.append('        contents:')
            lines.append(f'          - page: {label}')
            lines.append(f'            path: {top["path"]}')
            lines.append('            icon: fa-regular fa-landmark')
            continue
        if re.match(r'^Division \d+ Part \d+', label):
            lines.append(f'          - page: {label}')
            lines.append(f'            path: {top["path"]}')
            lines.append('            icon: fa-regular fa-book')
    lines.extend([
        '  - tab: changelog',
        '    layout:',
        '      - changelog: docs/changelog',
        'navbar-links:',
        '  - type: filled',
        '    text: Edit',
        '    url: https://dashboard.buildwithfern.com',
        'colors:',
        '  accent-primary:',
        '    light: "#FFFFFF"',
        '    dark: "#323A45"',
        '  background:',
        '    light: "#FFFFFF"',
        '    dark: "#323A45"',
        '  border:',
        '    light: "#FFFFFF"',
        '    dark: "#323A45"',
        'theme:',
        '  page-actions: toolbar',
        '  footer-nav: minimal',
        '  tabs: bubble',
        'logo:',
        '  dark: docs/assets/logo-dark.png',
        '  light: docs/assets/logo-light.png',
        '  height: 20',
        '  href: https://buildwithfern.com',
        'favicon: docs/assets/favicon.svg',
        'css:',
        '  - styles.css',
        '  - docs/assets/onboarding-theme.css',
        'js: custom.js',
        'typography:',
        '  headingsFont:',
        '    name: Inter',
        '  bodyFont:',
        '    name: Inter',
        'ai-search: {}',
    ])
    return '\n'.join(lines) + '\n'


def main():
    structure = json.loads(JSON_PATH.read_text()).get('california_family_code_structure', [])
    generated = write_pages(structure)
    DOCS_YML_PATH.write_text(build_docs_yaml(generated))
    print(f'Generated {len(generated)} pages from {len(structure)} divisions.')


if __name__ == '__main__':
    main()
