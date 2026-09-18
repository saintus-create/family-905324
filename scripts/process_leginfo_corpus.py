#!/usr/bin/env python3
"""
Process leginfo.legislature.ca.gov corpus into Fern-compatible format.
Creates MDX documentation pages and updates navigation.
"""

import json
import gzip
import os
import re
from pathlib import Path
from collections import defaultdict

# Configuration
LAW_DIR = Path("fern/data/law")
DOCS_DIR = Path("fern/docs/pages/legislation")
CODES = {
    "BPC": "Business & Professions Code",
    "CCP": "Code of Civil Procedure", 
    "CIV": "Civil Code",
    "COM": "Commercial Code",
    "CONS": "Constitution",
    "CORP": "Corporations Code",
    "EDC": "Education Code",
    "ELEC": "Elections Code",
    "EVID": "Evidence Code",
    "FAC": "Financial Code",
    "FAM": "Family Code",
    "FGC": "Food & Agricultural Code",
    "FIN": "Financial Code",  # Note: duplicate of FAC?
    "GOV": "Government Code",
    "HNC": "Harbors & Navigation Code",
    "HSC": "Health & Safety Code",
    "INS": "Insurance Code",
    "LAB": "Labor Code",
    "MVC": "Military & Veterans Code",
    "PCC": "Penal Code",
    "PEN": "Penal Code",  # Note: duplicate?
    "PRC": "Public Resources Code",
    "PROB": "Probate Code",
    "PUC": "Public Utilities Code",
    "RTC": "Revenue & Taxation Code",
    "SHC": "Strengthening Health Code",  # Note: verify this
    "UIC": "Unemployment Insurance Code",
    "VEH": "Vehicle Code",
    "WAT": "Water Code",
    "WIC": "Welfare & Institutions Code",
}

# Full names for codes
CODE_FULL_NAMES = {
    "BPC": "Business and Professions Code",
    "CCP": "Code of Civil Procedure",
    "CIV": "Civil Code",
    "COM": "Commercial Code",
    "CONS": "California Constitution",
    "CORP": "Corporations Code",
    "EDC": "Education Code",
    "ELEC": "Elections Code",
    "EVID": "Evidence Code",
    "FAC": "Financial Code",
    "FAM": "Family Code",
    "FGC": "Food and Agricultural Code",
    "FIN": "Financial Code",
    "GOV": "Government Code",
    "HNC": "Harbors and Navigation Code",
    "HSC": "Health and Safety Code",
    "INS": "Insurance Code",
    "LAB": "Labor Code",
    "MVC": "Military and Veterans Code",
    "PCC": "Penal Code",
    "PEN": "Penal Code",
    "PRC": "Public Resources Code",
    "PROB": "Probate Code",
    "PUC": "Public Utilities Code",
    "RTC": "Revenue and Taxation Code",
    "SHC": "Strengthening Health Code",
    "UIC": "Unemployment Insurance Code",
    "VEH": "Vehicle Code",
    "WAT": "Water Code",
    "WIC": "Welfare and Institutions Code",
}

def sanitize_filename(text):
    """Convert text to safe filename."""
    if text is None:
        return "unknown"
    text = str(text).strip()
    # Replace special characters
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', text)
    text = re.sub(r'\s+', '_', text)
    return text[:100]  # Limit length

def markdown_escape(text):
    """Escape special markdown characters."""
    if text is None:
        return ""
    text = str(text)
    text = text.replace('\\', '\\\\')
    text = text.replace('|', '\\|')
    text = text.replace('*', '\\*')
    text = text.replace('_', '\\_')
    text = text.replace('~', '\\~')
    return text

def create_code_overview(code, code_name, sections):
    """Create an overview page for a legal code."""
    content = f"""# {code_name}

This section contains the complete {code_name} from the California legislative website.

## Code Information

- **Code:** {code}
- **Total Sections:** {len(sections)}

## Divisions and Structure

"""
    
    # Group sections by division
    divisions = defaultdict(list)
    for section in sections:
        division = section.get('division', 'Uncategorized')
        divisions[division].append(section)
    
    for division, division_sections in sorted(divisions.items(), key=lambda x: x[0] or ''):
        content += f"\n### {markdown_escape(division or 'Uncategorized')}\n\n"
        content += "| Section | Title |\n"
        content += "|---------|-------|\n"
        for sec in sorted(division_sections, key=lambda x: x.get('section', '999999')):
            section_num = sec.get('section', 'Unknown')
            text_preview = sec.get('text', '')[:80].replace('\n', ' ').strip()
            content += f"| [{section_num}](./{code}/section_{section_num}.mdx) | {markdown_escape(text_preview)} |\n"
    
    content += "\n" + "---\n"
    content += "*Source: [California Legislative Information](https://leginfo.legislature.ca.gov/)*\n"
    
    return content

def create_section_page(code, section_data):
    """Create a page for a single legal section."""
    section_num = section_data.get('section', 'unknown')
    citation = section_data.get('citation', '')
    text = section_data.get('text', '')
    history = section_data.get('history', '')
    division = section_data.get('division', '')
    part = section_data.get('part', '')
    title = section_data.get('title', '')
    chapter = section_data.get('chapter', '')
    article = section_data.get('article', '')
    
    # Build hierarchy path
    hierarchy = []
    if division:
        hierarchy.append(f"Division: {division}")
    if part:
        hierarchy.append(f"Part: {part}")
    if title:
        hierarchy.append(f"Title: {title}")
    if chapter:
        hierarchy.append(f"Chapter: {chapter}")
    if article:
        hierarchy.append(f"Article: {article}")
    
    content = f"""# {citation}

"""
    
    if hierarchy:
        content += "**Hierarchy:** " + " > ".join(hierarchy) + "\n\n"
    
    content += f"**Citation:** {citation}\n\n"
    content += "---\n\n"
    
    content += f"## Text\n\n{text}\n\n"
    
    if history:
        content += f"## Legislative History\n\n{history}\n\n"
    
    content += "---\n"
    content += f"*Last updated: {section_data.get('last_updated', 'Unknown')}*\n"
    content += f"*Source: [California Legislative Information - {citation}](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode={code}&sectionNum={section_num})*\n"
    
    return content

def process_all_codes():
    """Process all legal code files."""
    # Create output directories
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process each code file
    for gz_file in LAW_DIR.glob("*.jsonl.gz"):
        code = gz_file.stem  # Remove .jsonl.gz
        print(f"Processing {code}...")
        
        # Read and parse the gzipped JSONL file
        sections = []
        with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    sections.append(data)
                except json.JSONDecodeError:
                    continue
        
        if not sections:
            print(f"  No valid sections found in {code}")
            continue
        
        # Get code name
        code_name = CODE_FULL_NAMES.get(code, f"{code} Code")
        
        # Create code directory
        code_dir = DOCS_DIR / code.lower()
        code_dir.mkdir(parents=True, exist_ok=True)
        
        # Create overview page
        overview_content = create_code_overview(code, code_name, sections)
        overview_path = code_dir / "index.mdx"
        with open(overview_path, 'w', encoding='utf-8') as f:
            f.write(overview_content)
        print(f"  Created overview: {overview_path}")
        
        # Create individual section pages
        for section in sections:
            section_num = section.get('section', 'unknown')
            if not isinstance(section_num, str):
                section_num = str(section_num)
            
            filename = f"section_{section_num}.mdx"
            filepath = code_dir / filename
            
            content = create_section_page(code, section)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"  Created {len(sections)} section pages for {code}")

def update_navigation():
    """Update the docs.yml navigation to include the new codes."""
    docs_yml = Path("fern/docs.yml")
    
    with open(docs_yml, 'r') as f:
        content = f.read()
    
    # Find the Legislation section and add codes there
    # We'll add a new subsection for "California Codes"
    
    legislation_marker = "  - section: Legislation\n    collapsed: true\n    contents:"
    
    if legislation_marker in content:
        # Insert after the Legislation section start
        parts = content.split(legislation_marker)
        
        codes_nav = """      - page: California Codes Overview
        path: ./docs/pages/legislation/index.mdx
        icon: book
      - section: California Codes
        collapsed: true
        contents:
"""
        
        # Add each code to navigation
        for code, code_name in sorted(CODE_FULL_NAMES.items()):
            codes_nav += f"""        - page: {code_name}
          path: ./docs/pages/legislation/{code.lower()}/index.mdx
          icon: file-text
"""
        
        new_content = legislation_marker.join([parts[0], codes_nav + parts[1]])
        
        with open(docs_yml, 'w') as f:
            f.write(new_content)
        
        print("Updated navigation in docs.yml")
    else:
        print("Could not find Legislation section in docs.yml")

if __name__ == "__main__":
    print("Processing leginfo corpus...")
    process_all_codes()
    update_navigation()
    print("Done!")
