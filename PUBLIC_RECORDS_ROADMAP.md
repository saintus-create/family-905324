# Public Records Corpus Expansion Roadmap

We have successfully integrated a new **Public Records** branch into the existing Fern documentation site. This branch acts as the authoritative, source-traceable repository for data on law enforcement agencies, training, contractors, funding, and civil payouts in California.

## Phase 1: Foundation (Completed)
- **Scope Definition**: Established strict provenance rules requiring all data to be traceable to primary public sources (e.g., POST portals, municipal contracts, state grant databases). Excluded unverified claims and private information.
- **Navigation Integration**: Added a dedicated `Public Records` tab to the Fern `docs.yml` navigation, housing pages for Agencies, POST Training, Contractors, Funding, and Civil Payouts.
- **Data Model & Ingestion**: Designed a unified `PUBLIC_RECORDS.json` data model. Created a Python generator (`generate_public_records_docs.py`) to convert this JSON into structured MDX pages.
- **Initial Dataset**: Seeded the database with initial vendor contract data for Performa Labs Inc. (Garden Grove, Baldwin Park, Pasadena) to validate the pipeline.

## Phase 2: Automated Ingestion (Next Steps)
To scale the corpus, we need to build automated extraction scripts that populate `PUBLIC_RECORDS.json`:
1.  **POST Data Extractor**: Script to query the California POST Open Data API/CSVs to map all certified agencies and training providers.
2.  **BSCC Grant Extractor**: Script to parse Board of State and Community Corrections (BSCC) award announcements (e.g., Prop 47, Prop 64) and VAWA allocations.
3.  **Municipal Contract Aggregator**: Tool to parse municipal legislative portals (Granicus/NovusAgenda) for target vendor keywords (e.g., "Northpointe", "Performa Labs").
4.  **Misconduct & Settlement Integration**: Cross-reference the newly launched California Police Misconduct Records Database with municipal budget disclosures on civil litigation payouts.

## Phase 3: GitHub Actions Automation
- Integrate the new extraction scripts into the existing `.github/workflows/` directory.
- Schedule the pipeline to run weekly, ensuring the public records data remains fresh and automatically publishes to the Fern site alongside the legal feed.

## Phase 4: Platform Migration (Future)
Once the data pipelines are robust and the Fern site contains the complete, authoritative corpus, we will resume the migration to **Fumadocs + Managed AI Search (Inkeep)** to provide a polished UI and grounded AI research assistance without the burden of custom visual maintenance.
