import requests
import json
import os
import re
from bs4 import BeautifulSoup

def fetch_agencies():
    url = "https://en.wikipedia.org/w/api.php?action=parse&page=List_of_law_enforcement_agencies_in_California&format=json&prop=text"
    response = requests.get(url, headers={"User-Agent": "ManusAgent/1.0"}).json()
    html = response['parse']['text']['*']
    soup = BeautifulSoup(html, 'html.parser')
    
    agencies = []
    # Find all list items
    for li in soup.find_all('li'):
        text = li.text.strip()
        # Clean up citation markers like [1]
        text = re.sub(r'\[\d+\]', '', text).strip()
        
        if 'Police Department' in text or 'Sheriff' in text or 'Department of' in text:
            # Skip navigation elements and table of contents
            if '^' in text or 'Jump to' in text or text.startswith('v') or text.startswith('t') or text.startswith('e'):
                continue
                
            if len(text) > 10 and len(text) < 100:
                agencies.append(text)
                
    return list(dict.fromkeys(agencies)) # Remove duplicates

def main():
    print("Fetching agencies from Wikipedia...")
    agencies_list = fetch_agencies()
    print(f"Found {len(agencies_list)} potential agencies.")
    
    # Format for our DB
    formatted_agencies = []
    for agency in agencies_list:
        # Determine type
        agency_type = "Municipal Police"
        if "Sheriff" in agency:
            agency_type = "County Sheriff"
        elif "State" in agency or "Department of" in agency or "Highway Patrol" in agency:
            agency_type = "State Agency"
        elif "University" in agency or "College" in agency or "School" in agency:
            agency_type = "Campus Police"
        elif "Transit" in agency or "BART" in agency or "Airport" in agency:
            agency_type = "Transit/Airport Police"
            
        # Basic ID generation
        agency_id = "agency_" + re.sub(r'[^a-z0-9]', '_', agency.lower())
        agency_id = re.sub(r'_+', '_', agency_id).strip('_')
        
        formatted_agencies.append({
            "id": agency_id,
            "name": agency,
            "type": agency_type,
            "county": "Unknown", # We'll need a better geocoder later
            "post_certified": True, # Assumption for now
            "funding": [],
            "contracts": [],
            "settlements": []
        })
    
    # Save the raw list for review
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, 'AGENCIES_EXTRACT.json')
    
    with open(output_path, 'w') as f:
        json.dump(formatted_agencies, f, indent=2)
        
    print(f"Saved {len(formatted_agencies)} agencies to {output_path}")

if __name__ == "__main__":
    main()
