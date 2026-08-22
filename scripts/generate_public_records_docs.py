import json
import os

def load_db(path):
    with open(path, 'r') as f:
        return json.load(f)

def generate_agencies_mdx(db, output_path):
    content = "# Police & Sheriff Agencies\n\n"
    content += "This index tracks law enforcement agencies in California, providing structured data on their contracts, funding, and POST certification status based on public records.\n\n"
    
    for agency in db.get('agencies', []):
        content += f"## {agency['name']}\n\n"
        content += f"- **Type**: {agency['type']}\n"
        content += f"- **County**: {agency['county']}\n"
        content += f"- **POST Certified**: {'Yes' if agency['post_certified'] else 'No'}\n\n"
        
        if agency.get('contracts'):
            content += "### Known Contracts\n\n"
            for contract in agency['contracts']:
                amount_str = f"${contract['amount']:,}" if contract['amount'] else "Amount undisclosed"
                content += f"- **{contract['vendor']}** ({contract['year']}): {contract['purpose']} — {amount_str}. [Source]({contract['citation']})\n"
            content += "\n"
            
        if agency.get('funding'):
            content += "### Funding & Grants\n\n"
            for fund in agency['funding']:
                amount_str = f"${fund['amount']:,}" if fund['amount'] else "Amount undisclosed"
                content += f"- **{fund['source']}** ({fund['year']}): {amount_str}. [Source]({fund['citation']})\n"
            content += "\n"
            
    with open(output_path, 'w') as f:
        f.write(content)

def generate_contractors_mdx(db, output_path):
    content = "# Public Safety Contractors\n\n"
    content += "This index tracks private entities receiving public funds for law enforcement technology, training, or services, based on publicly available contracts and vendor disclosures.\n\n"
    
    agency_map = {a['id']: a['name'] for a in db.get('agencies', [])}
    
    for vendor in db.get('vendors', []):
        content += f"## {vendor['name']}\n\n"
        
        if vendor.get('services'):
            content += "### Services Provided\n\n"
            for service in vendor['services']:
                content += f"- {service}\n"
            content += "\n"
            
        if vendor.get('known_contracts'):
            content += "### Known Agency Contracts\n\n"
            for agency_id in vendor['known_contracts']:
                agency_name = agency_map.get(agency_id, agency_id)
                content += f"- {agency_name}\n"
            content += "\n"
            
    with open(output_path, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'PUBLIC_RECORDS.json')
    agencies_path = os.path.join(base_dir, 'fern', 'docs', 'pages', 'police-agencies.mdx')
    contractors_path = os.path.join(base_dir, 'fern', 'docs', 'pages', 'contractors.mdx')
    
    if os.path.exists(db_path):
        db = load_db(db_path)
        generate_agencies_mdx(db, agencies_path)
        generate_contractors_mdx(db, contractors_path)
        print("Successfully generated Public Records MDX pages.")
    else:
        print(f"Database not found at {db_path}")
