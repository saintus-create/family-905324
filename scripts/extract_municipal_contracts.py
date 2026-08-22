import requests
import json
import os
import datetime

# Known California clients on Legistar Web API (Reduced for speed)
LEGISTAR_CLIENTS = [
    "oakland",
    "sacramento",
    "fresno"
]

VENDORS = [
    "Northpointe",
    "Equivant",
    "Axon",
    "Flock Safety",
    "ShotSpotter",
    "Mark43",
    "Lexipol"
]

def search_legistar(client, vendor):
    # OData filter syntax for Legistar Web API
    url = f"https://webapi.legistar.com/v1/{client}/matters?$filter=substringof('{vendor}',MatterTitle) or substringof('{vendor}',MatterBodyName)"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
    except Exception as e:
        print(f"Error querying {client} for {vendor}: {e}")
    return []

def main():
    print("Starting municipal contract extraction via Legistar API...")
    results = []
    
    for client in LEGISTAR_CLIENTS:
        print(f"Querying client: {client}")
        for vendor in VENDORS:
            matters = search_legistar(client, vendor)
            if matters:
                print(f"  Found {len(matters)} records for {vendor} in {client}")
                for matter in matters:
                    # Create a standardized contract record
                    record = {
                        "source_system": "Legistar",
                        "client_id": client,
                        "vendor_keyword": vendor,
                        "matter_id": matter.get("MatterId"),
                        "matter_file": matter.get("MatterFile"),
                        "title": matter.get("MatterTitle"),
                        "status": matter.get("MatterStatusName"),
                        "date": matter.get("MatterPassedDate") or matter.get("MatterIntroDate"),
                        "body_name": matter.get("MatterBodyName"),
                        "extraction_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "url": f"https://{client}.legistar.com/LegislationDetail.aspx?ID={matter.get('MatterId')}&GUID={matter.get('MatterGuid')}"
                    }
                    results.append(record)
                    
    # Save the raw extraction results
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, 'MUNICIPAL_CONTRACTS_EXTRACT.json')
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Extraction complete. Found {len(results)} total potential contract records.")
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()
