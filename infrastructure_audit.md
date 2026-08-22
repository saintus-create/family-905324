# Infrastructure Audit & Optimization Plan

## 1. Architecture Overview
- **Core Technology**: The project uses [Fern](https://buildwithfern.com/) to generate documentation sites, likely focusing on California Family Law, Rules of Court, and legislation.
- **Data Generation Pipeline**: Python scripts (`rules_generator.py`, `generate_family_code_docs.py`) parse JSON/HTML into Markdown (`.mdx`) files stored in `fern/docs/pages/`.
- **CI/CD Pipeline**: GitHub Actions are used for multiple tasks:
  - `publish-docs.yml`: Deploys the Fern site to production when pushed to `main`.
  - `preview-docs.yml`: Generates preview environments.
  - `update-california-legislation.yml`: Scrapes legislation.
  - `update-invitations-to-comment.yml`: Scrapes active proposals.
  - `update-legal-feed.yml`: Scrapes a live legal feed.

## 2. Infrastructure Risks & Disjointed Components
1. **Missing Dependency Management**: 
   - There is no `requirements.txt`, `pyproject.toml`, or `Pipfile` for Python dependencies. Scripts import standard libraries, but if future packages (like `requests` or `beautifulsoup4`) are needed, there is no reproducible environment.
   - There is no `package.json` for Node.js dependencies, even though Fern relies on Node.
2. **Hardcoded Configurations**: 
   - Scripts like `update_california_legislation.py` write directly to specific file paths without environment variable overrides for different environments.
3. **Redundant Script Execution**:
   - Python scripts in GitHub actions execute inline scripts (e.g., `update-legal-feed.yml` has a massive inline Python script) instead of keeping them modular in the `scripts/` directory.
4. **Git Repository Bloat**:
   - Large JSON files (`RULES_OF_COURT.json`, `tableofcontents.json`) are committed directly to the repo. Over time, this will bloat the git history.
5. **Lack of Tests**:
   - There are no tests for the Python scripts that generate the MDX files. If the source HTML format changes, the scripts will fail silently or generate broken Markdown.

## 3. High-Priority Infrastructure Improvements
1. **Consolidate Python Dependencies**: Create a `requirements.txt` or `pyproject.toml` to explicitly define the Python environment.
2. **Extract Inline Scripts**: Move the large inline Python script from `update-legal-feed.yml` into a dedicated file in the `scripts/` directory.
3. **Implement Dependency Caching**: Update GitHub Actions to cache Python and Node dependencies to speed up execution.
4. **Add Gitignore Rules**: Ensure generated files and `__pycache__` are properly ignored.

---

I will implement these high-priority, safe changes.
