# California Family Law Corpus Improvement Roadmap

The current repository provides a solid structural foundation: it pulls from primary legislative and judicial sources (California Rules of Court, Family Code, legislative bills, and active proposals) and formats them into a static, readable site via Fern. However, to transition from a static reference site to a comprehensive, high-utility research corpus, the data ingestion, coverage, and structure must evolve.

This roadmap outlines a staged approach to improving the corpus across four dimensions: **Coverage & Authority**, **Freshness & Automation**, **Structure & Interconnectivity**, and **Retrieval & Analysis**.

## 1. Coverage & Authority Expansion

The current corpus relies heavily on statutory text and rulebooks. A robust legal research corpus requires authoritative interpretation and application context. To achieve the "Computational dialectics" and "Empirical research" goals stated in the documentation, the underlying data must expand beyond black-letter law.

### High-Priority Expansions

The most critical gap in the current corpus is binding case law. To provide true analytical value, the repository must integrate published decisions from the California Courts of Appeal and the California Supreme Court that interpret the Family Code. This can be implemented by pulling from authoritative open-access legal databases, such as CourtListener or the Free Law Project, using a scheduled ingestion script.

Furthermore, while the state-wide Rules of Court are present, family law practice is heavily dictated by county-level local rules. The corpus should expand to include targeted scrapers for the local family law rules of the most populous California counties, such as Los Angeles, San Diego, and Santa Clara. Finally, because family law is highly form-driven, the corpus should index and make searchable the metadata and instructions for mandatory Judicial Council forms (specifically the FL-series).

## 2. Freshness & Automation Enhancements

Legal information decays rapidly. The current GitHub Actions provide a good baseline for legislative updates, but the core statutory text appears to be static. 

To ensure ongoing accuracy, the `RULES_OF_COURT.json` and Family Code text should not remain static files. The repository needs a pipeline to regularly diff the official California Legislative Information site against the local corpus, automatically proposing pull requests for statutory amendments. Additionally, the existing `update-legal-feed.yml` workflow should be expanded to specifically flag and ingest newly published family law appellate decisions as they are released. To prevent silent failures in these automated processes, the infrastructure requires automated tests that run weekly to verify that the source URLs used by the scrapers have not changed their DOM structure.

## 3. Structure & Interconnectivity

A corpus is only as useful as its internal connections. Currently, the rules and code exist as siloed text blocks.

The corpus must implement bidirectional citation linking. By parsing the text of the Family Code and Rules of Court to identify cross-references (for example, phrases like "pursuant to Section 4320"), the build process can automatically convert these into hyperlinks within the Fern site. This should be paired with semantic tagging, applying a standardized taxonomy to the corpus to tag rules, statutes, and cases with concepts like child custody, spousal support, or domestic violence. Ultimately, this interconnected data can be used to build upon the existing "Defense Authority Graph" concept by programmatically generating Mermaid.js diagrams that map the relationships between a statute, its implementing rule of court, and its key interpreting cases.

## 4. Retrieval & Analysis Readiness

To support the computational dialectics and empirical research goals mentioned in the site's navigation, the corpus must be structured for machine reading, not just human reading.

The repository should introduce a vectorization pipeline to prepare the corpus for semantic search and retrieval-augmented generation (RAG). This would involve a GitHub Action that chunks the Markdown files, generates embeddings, and stores them in a vector database. While Fern generates an excellent user interface, the underlying JSON data should also be exposed via a simple API or clearly documented raw data endpoints so researchers can query the corpus programmatically. Finally, the corpus needs version history tracking to maintain a clear, queryable record of how specific Family Code sections have changed over time, allowing researchers to view the law exactly as it existed on a specific date.
