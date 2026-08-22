# Public Records Research Scope

The California Family Law Research site is expanding to include a dedicated public-records branch. This branch tracks police agencies, training providers, contractors, payouts, and funding flows.

## 1. Domain Boundaries

The expansion covers **public institutional records**, specifically:
*   **Law Enforcement Agencies**: Police departments, sheriff's offices, and related public safety entities in California.
*   **Training & Certification**: POST (Peace Officer Standards and Training) data, certified training providers, and curriculum records.
*   **Contractors & Vendors**: Entities receiving public funds for law enforcement technology, training, or services (e.g., Northpointe Inc., Performa Labs Inc.).
*   **Funding & Grants**: Federal, state, and local funding allocations to these agencies, including VAWA (Violence Against Women Act) grants, the State Budget Act, and local municipal allocations.
*   **Payouts & Settlements**: Publicly disclosed civil settlements, judgments, and payouts related to law enforcement agencies.

## 2. Provenance and Traceability

Every record in this branch must be explicitly traceable to a primary public source:
*   State and federal grant databases (e.g., US DOJ, California Board of State and Community Corrections).
*   State controller or municipal budget transparency portals.
*   POST open data portals or published rosters.
*   Publicly available vendor contracts, board of supervisors minutes, or city council agendas.
*   Court records or official municipal disclosures for settlements.

**Rule**: If a data point cannot be cited to a specific, retrievable public record, it cannot be included in the structured corpus.

## 3. Safety and Policy Constraints

*   **No Private Information**: The corpus will only index institutional, vendor, and public-employee data that is already a matter of public record. It will not aggregate private residential addresses, family members, or non-public personal data of officers or individuals.
*   **No Unverified Claims**: Allegations of misconduct or vendor failure must be sourced to official findings, court judgments, or formal audits—not unverified third-party aggregation.
*   **Analysis vs. Fact**: The site will present the data (e.g., "Agency X received $Y in VAWA funding in 2024"). It will not automatically generate causal claims (e.g., "Agency X received $Y *because* of Z") unless that causality is explicitly stated in the primary source document.

## 4. Next Steps

The immediate next phase is to identify the specific, machine-readable primary sources (APIs, CSVs, official scrapable portals) for POST data, VAWA allocations, and California municipal payouts to begin designing the ingestion pipeline.
