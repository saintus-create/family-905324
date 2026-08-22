import json
import os
import re

def build_db():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    extract_path = os.path.join(base_dir, 'AGENCIES_EXTRACT.json')
    contracts_path = os.path.join(base_dir, 'MUNICIPAL_CONTRACTS_EXTRACT.json')
    db_path = os.path.join(base_dir, 'PUBLIC_RECORDS.json')
    
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            current_db = json.load(f)
    else:
        current_db = {"agencies": [], "vendors": []}
        
    # Load extracted agencies if needed
    # ...
    
    # Process extracted contracts
    if os.path.exists(contracts_path):
        with open(contracts_path, 'r') as f:
            contracts = json.load(f)
            
        # Map clients to agencies (simple mapping for now)
        client_to_agency = {
            "oakland": "agency_oakland_police_department",
            "sacramento": "agency_sacramento_police_department",
            "fresno": "agency_fresno_police_department"
        }
        
        # Make sure the target agencies exist in the DB
        agency_map = {a['id']: a for a in current_db['agencies']}
        for agency_id in client_to_agency.values():
            if agency_id not in agency_map:
                name_parts = agency_id.replace('agency_', '').split('_')
                name = ' '.join([p.capitalize() for p in name_parts])
                new_agency = {
                    "id": agency_id,
                    "name": name,
                    "type": "Municipal Police",
                    "county": "Unknown",
                    "post_certified": True,
                    "funding": [],
                    "contracts": [],
                    "settlements": []
                }
                current_db['agencies'].append(new_agency)
                agency_map[agency_id] = new_agency
                
        # Add vendors if they don't exist
        existing_vendors = {v['name']: v for v in current_db['vendors']}
        
        # Add contracts to agencies
        agency_map = {a['id']: a for a in current_db['agencies']}
        
        for contract in contracts:
            if contract['status'] not in ['Passed', 'Adopted', 'Approved']:
                continue
                
            client_id = contract['client_id']
            agency_id = client_to_agency.get(client_id)
            
            if not agency_id:
                continue
                
            vendor_name = contract['vendor_keyword']
            if vendor_name == "Flock Safety":
                vendor_name = "Flock Safety"
            elif vendor_name == "Axon":
                vendor_name = "Axon Enterprise Inc."
            elif vendor_name == "ShotSpotter":
                vendor_name = "ShotSpotter (SoundThinking)"
            elif vendor_name == "Northpointe":
                vendor_name = "Northpointe Inc. (Equivant)"
            elif vendor_name == "Lexipol":
                vendor_name = "Lexipol"
                
            # Ensure vendor exists
            if vendor_name not in existing_vendors:
                new_vendor = {
                    "id": f"vendor_{vendor_name.lower().replace(' ', '_').replace('.', '').replace('(', '').replace(')', '')}",
                    "name": vendor_name,
                    "services": ["Law enforcement technology and services"],
                    "known_contracts": []
                }
                current_db['vendors'].append(new_vendor)
                existing_vendors[vendor_name] = new_vendor
                
            # Add agency to vendor's known contracts
            if agency_id not in existing_vendors[vendor_name]['known_contracts']:
                existing_vendors[vendor_name]['known_contracts'].append(agency_id)
                
            # Add contract to agency
            if agency_id in agency_map:
                agency = agency_map[agency_id]
                
                # Extract amount if possible (very basic regex)
                amount = None
                amount_match = re.search(r'\$([0-9,]+)', contract['title'])
                if amount_match:
                    try:
                        amount = int(amount_match.group(1).replace(',', ''))
                    except:
                        pass
                        
                # Check if we already have this contract
                contract_exists = False
                for existing in agency.get('contracts', []):
                    if existing['citation'] == contract['url']:
                        contract_exists = True
                        break
                        
                if not contract_exists:
                    year = int(contract['date'][:4]) if contract['date'] else None
                    agency['contracts'].append({
                        "vendor": vendor_name,
                        "purpose": contract['title'][:150] + "..." if len(contract['title']) > 150 else contract['title'],
                        "amount": amount,
                        "year": year,
                        "citation": contract['url']
                    })
                    
    # Save the updated DB
    with open(db_path, 'w') as f:
        json.dump(current_db, f, indent=2)
        
    print(f"Database updated with {len(contracts)} extracted contracts.")

if __name__ == "__main__":
    build_db()
