import json
import os

def build_db():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    extract_path = os.path.join(base_dir, 'AGENCIES_EXTRACT.json')
    db_path = os.path.join(base_dir, 'PUBLIC_RECORDS.json')
    
    # Load the current DB (which has our seed contracts)
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            current_db = json.load(f)
    else:
        current_db = {"agencies": [], "vendors": []}
        
    # Load the extracted agencies
    if os.path.exists(extract_path):
        with open(extract_path, 'r') as f:
            extracted_agencies = json.load(f)
    else:
        print("No extracted agencies found.")
        return
        
    # Merge agencies
    existing_agency_ids = {a['id']: a for a in current_db['agencies']}
    
    # Update existing or add new
    for agency in extracted_agencies:
        if agency['id'] in existing_agency_ids:
            # Keep the existing one (it has our contracts) but maybe update name
            pass
        else:
            # Only add a subset to avoid overwhelming the MDX for now, let's take the first 50
            if len(current_db['agencies']) < 50:
                current_db['agencies'].append(agency)
                existing_agency_ids[agency['id']] = agency
                
    # Save the updated DB
    with open(db_path, 'w') as f:
        json.dump(current_db, f, indent=2)
        
    print(f"Database built with {len(current_db['agencies'])} agencies and {len(current_db['vendors'])} vendors.")

if __name__ == "__main__":
    build_db()
