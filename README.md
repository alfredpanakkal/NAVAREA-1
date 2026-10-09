# NAVAREA I: Deterministic Scraper & Parser Pipeline

This repository hosts a Python-based autonomous data pipeline designed to ingest, deterministically parse, and synchronize "NAVAREA I" radio navigational warnings from the United Kingdom Hydrographic Office (UKHO) directly into the **Helm.Warning** maritime database architecture.

It utilizes the highly adaptive **[Scrapling](https://github.com/D4Vinci/Scrapling)** framework for robust anti-bot bypass and element extraction.

## Architectural Alignment

This pipeline is fully compliant with the **Helm.Warning 4-Stage Architecture**, successfully implementing the required 6 Parameter Domains (Identity, Temporal, Spatial, Hazard, Evidence, and Governance).

### Pipeline Components

1. **The Evidence Locker (`navarea_scraper.py`)**
   - Fetches the active warning repository (`https://msi.admiralty.co.uk/RadioNavigationalWarnings`).
   - Navigates the DOM to extract required session verification tokens.
   - Emulates user behavior to submit the "Show selection" form specifically for NAVAREA I warnings.
   - Outputs an immutable `navarea_1_warnings.txt` payload.

2. **The Multi-Pass Deterministic Parser (`navarea_parser.py`)**
   - **Coordinate Normalization:** Extracts text-based DMS coordinates (e.g., `52-07.7N 003-56.4E`) and converts them into rigorous WGS 84 Decimal Degrees (`latitude`, `longitude`).
   - **GeoJSON Generation:** Automatically computes `spatial` column properties (Point, LineString).
   - **Semantic Hazard Tagging:** Classifies warnings via keyword analysis (`aton`, `military`, `subsea`, `drifting`, `offshore`).
   - **Cryptographic Traceability:** Generates `checksum_sha256` hashes for every raw message block.
   - Outputs a segregated, database-ready `parsed_warnings.json` file.

3. **Dual-Route Database Router (`supabase_sync.py`)**
   - Ingests the normalized JSON payload.
   - Synchronizes directly with the production Supabase project via `supabase-py`.
   - Safely batches and `upserts` records into the official `public.raw_messages` (Stage 3) and `public.nav_warnings` (Stage 4) master tables.

## Usage & Execution

### 1. Local Environment Setup
Since this repository includes the Scrapling source code directly, install the local framework alongside the required network and database libraries:
```bash
pip install -e .[all]
pip install requests supabase
```

### 2. Manual Execution
Run the pipeline stages sequentially:
```bash
# 1. Fetch the raw payload
python navarea_scraper.py

# 2. Extract and normalize GeoJSON & Semantics
python navarea_parser.py

# 3. Synchronize with Supabase
# Requires SUPABASE_URL and SUPABASE_KEY environment variables
python supabase_sync.py
```

### 3. Automated Cloud Pipeline (GitHub Actions)
This repository includes a pre-configured CI/CD workflow (`.github/workflows/navarea-test.yml`). 
Upon every push to the main branch, a GitHub Action automatically provisions an Ubuntu runner, installs dependencies, executes the scraper, verifies the deterministic parser's JSON structure, and initiates a secure sync to the Supabase database (provided repository secrets are set).

---

## Acknowledgments & Credits

**Scrapling Library**  
This repository originated as a fork of [Scrapling](https://github.com/D4Vinci/Scrapling), an adaptive web scraping framework. All credit for the underlying scraping framework, fetcher engines, and DOM selectors goes to the original creator **Karim Shoair (D4Vinci)** and the contributors to the Scrapling project.

* [Scrapling GitHub Repository](https://github.com/D4Vinci/Scrapling)
* [Scrapling Documentation](https://scrapling.readthedocs.io)
