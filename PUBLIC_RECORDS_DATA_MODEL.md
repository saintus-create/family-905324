# Public Records Data Model & Ingestion Architecture

To integrate the new public records domain into the existing Fern documentation site, we will use a JSON-to-MDX pipeline similar to the existing `generate_family_code_docs.py` script. 

## 1. Unified JSON Data Model

The ingestion scripts will aggregate data from primary sources into a structured `PUBLIC_RECORDS.json` file. This file will serve as the single source of truth for the public records branch.

```json
{
  "agencies": [
    {
      "id": "agency_123",
      "name": "Garden Grove Police Department",
      "type": "Municipal Police",
      "county": "Orange",
      "post_certified": true,
      "funding": [
        {
          "source": "BSCC Prop 47",
          "amount": 1500000,
          "year": 2024,
          "citation": "https://www.bscc.ca.gov/..."
        }
      ],
      "contracts": [
        {
          "vendor": "Performa Labs Inc.",
          "purpose": "Subscription-based training course software",
          "amount": 94600,
          "year": 2024,
          "citation": "https://gardengrove.novusagenda.com/..."
        }
      ],
      "settlements": []
    }
  ],
  "vendors": [
    {
      "id": "vendor_456",
      "name": "Performa Labs Inc.",
      "services": ["POST-approved mobile training app", "De-escalation training tools"],
      "known_contracts": ["agency_123", "agency_789"]
    }
  ]
}
```

## 2. Ingestion Architecture

The pipeline will consist of three stages:

### Stage 1: Extraction (Python Scrapers)
We will build modular Python scripts to extract data from target sources:
*   `scripts/extract_agencies.py`: Extracts the canonical list of California law enforcement agencies from Wikipedia (acting as a proxy until the POST Open Data API is accessible).
*   `scripts/extract_bscc_grants.py`: Scrapes BSCC grant award announcements.
*   `scripts/extract_municipal_contracts.py`: Parses known Granicus/NovusAgenda portals for specific vendor keywords (e.g., "Performa Labs", "Northpointe").

### Stage 2: Transformation & Validation
A central script, `scripts/build_public_records_db.py`, will take the raw extracts, validate them against the provenance constraints (ensuring every data point has a valid URL citation), and compile them into `PUBLIC_RECORDS.json`.

### Stage 3: Generation (MDX Output)
A generator script, `generate_public_records_docs.py`, will read `PUBLIC_RECORDS.json` and generate the MDX files for the Fern frontend:
*   `fern/docs/pages/police-agencies.mdx` (Table of agencies with funding/contract summaries)
*   `fern/docs/pages/contractors.mdx` (Vendor profiles with linked contracts)
*   `fern/docs/pages/funding-grants.mdx` (Aggregated funding flows)

## 3. GitHub Actions Integration

The extraction and generation scripts will be added to the existing GitHub Actions scheduled workflows (`.github/workflows/`), ensuring the public records corpus is automatically refreshed alongside the legal feed and legislative updates.
