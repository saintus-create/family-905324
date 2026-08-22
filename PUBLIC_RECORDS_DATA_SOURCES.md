# Public Records Data Sources & Ingestion Strategy

This document outlines the authoritative primary sources identified for the public records corpus expansion.

## 1. POST Training & Certification
**Source**: California POST Open Data Portal (opendata.post.ca.gov)
*   **Data Available**: Law enforcement agency statistics, demographics, and certified training courses.
*   **Ingestion Strategy**: The California POST Open Data portal and Data Warehouse provide statistics on peace officers and training courses. We will need to query the POST API or download structured datasets (CSVs) to map certified providers and agency compliance.

## 2. Law Enforcement Agencies & Contractors
**Sources**: 
*   California Open Data Portal (data.ca.gov)
*   Municipal Open Data Portals (e.g., San Francisco DataSF, San Diego Open Data, San Jose Open Data)
*   California State Contracts Registry
*   City Council / Board of Supervisors Meeting Minutes (e.g., Granicus platforms)
*   **Targeted Search (Performa Labs / Northpointe)**: Vendor contracts are typically approved at the municipal level. For example, a Garden Grove city council coversheet indicates a $94,600 agreement with Performa-Labs, and Baldwin Park's Granicus system holds a staff report on their mobile app for POST-approved training.
*   **Ingestion Strategy**: Aggregate vendor contracts from municipal legislative management systems (like Granicus/NovusAgenda) and state contract registries.

## 3. Funding & Grants (VAWA, BSCC)
**Sources**:
*   Board of State and Community Corrections (BSCC) - administers hundreds of millions in grants annually (e.g., CPGP, Prop 47, Prop 64).
*   Office on Violence Against Women (OVW) - federal grant awards announcements.
*   **Ingestion Strategy**: Scrape BSCC grant award announcements and OVW federal press releases to track allocations to California law enforcement agencies.

## 4. Civil Settlements & Payouts
**Sources**:
*   California Police Misconduct Records Database (recently launched, indexing 12,000 cases of misconduct and use-of-force).
*   Police Funding Database (policefundingdatabase.org) - tracks settlements resulting in policy changes and monetary compensation.
*   **Ingestion Strategy**: Cross-reference the new California police misconduct database with municipal budget disclosures on civil litigation payouts.

## Next Steps for Data Architecture
The next phase is to design a unified JSON/Markdown data model that can ingest these disparate sources (POST CSVs, Granicus contract PDFs, BSCC grant lists) and output structured MDX files for the Fern frontend.
