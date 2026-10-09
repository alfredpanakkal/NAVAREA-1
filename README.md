# NAVAREA I: Deterministic Scraper & Parser Pipeline

[![NAVAREA Scraper Pipeline](https://github.com/alfredpanakkal/NAVAREA-1/actions/workflows/navarea-test.yml/badge.svg)](https://github.com/alfredpanakkal/NAVAREA-1/actions/workflows/navarea-test.yml)
[![Production Portal](https://img.shields.io/badge/Production%20Portal-Helm.Warning%20Data%20Bank-0070f3?style=flat&logo=vercel)](https://helmwarning.vercel.app/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com)

> **Official Ingestion Pipeline for [Helm.Warning — NAVAREA Data Bank](https://helmwarning.vercel.app/)**

This repository hosts a Python-based autonomous data pipeline designed to ingest, deterministically parse, normalize, and synchronize active **NAVAREA I** radio navigational warnings from the United Kingdom Hydrographic Office (UKHO) directly into the **Helm.Warning** maritime database architecture.

It utilizes the adaptive **[Scrapling](https://github.com/D4Vinci/Scrapling)** framework for robust anti-bot bypass, stealth session handling, and DOM extraction.

---

## 🌐 Production Platform
- **Live Data Bank & Map Portal:** [https://helmwarning.vercel.app/](https://helmwarning.vercel.app/)
- **Authority / Source:** United Kingdom Hydrographic Office (UKHO) / Admiralty MSI
- **Coverage Zone:** NAVAREA I (North Sea, English Channel, NE Atlantic)

---

## 🏗️ Architectural Alignment

This pipeline is fully compliant with the **Helm.Warning 4-Stage Architecture**, adhering to the required 6 Parameter Domains (Identity, Temporal, Spatial, Hazard, Evidence, and Governance).

```
[ Authoritative Hydrographic Feeds: UKHO Admiralty MSI ]
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│             STAGE 1 & 2: SCRAPE & VERIFICATION              │
│  navarea_scraper.py (Session Token + In-Force Selection)    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          STAGE 2: MULTI-PASS DETERMINISTIC PARSER           │
│  navarea_parser.py (WGS84 Coordinates, GeoJSON, Semantics)  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│     STAGE 3 & 4: DUAL-ROUTE SUPABASE SYNCHRONIZATION        │
│  supabase_sync.py                                           │
│  ├── public.raw_messages (Immutable Audit Log)              │
│  └── public.nav_warnings (Master In-Force Spatial Records)  │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline Components

1. **The Evidence Locker (`navarea_scraper.py`)**
   - Fetches the active warning repository (`https://msi.admiralty.co.uk/RadioNavigationalWarnings`).
   - Resolves CSRF verification tokens dynamically.
   - Submits the form selection specifically for all in-force NAVAREA I warnings.
   - Emits an untouched, verbatim `navarea_1_warnings.txt` payload.

2. **The Multi-Pass Deterministic Parser (`navarea_parser.py`)**
   - **Coordinate Normalization:** Extracts text-based DMS / DM coordinates (e.g., `52-07.7N 003-56.4E`) and converts them into decimal degrees (`latitude`, `longitude`).
   - **GeoJSON Generation:** Automatically creates WGS 84 `spatial` features (Point, LineString).
   - **Hazard Semantic Classification:** Tags warnings using maritime keywords (`aton`, `military`, `subsea`, `drifting`, `offshore`).
   - **Affected Charts:** Captures referenced Admiralty/INT charts (e.g., `INT 102`, `CHART GB 4102`).
   - **Cryptographic Traceability:** Generates `checksum_sha256` hashes for every bulletin block.
   - Emits structured `parsed_warnings.json`.

3. **Dual-Route Database Router (`supabase_sync.py`)**
   - Consumes the normalized JSON payload.
   - Interacts with Supabase using `supabase-py`.
   - Idempotently upserts records into `public.raw_messages` and `public.nav_warnings` keyed on `(warning_id, source_id)`.

---

## 🚀 Usage & Execution

### 1. Local Setup
Clone the repository and install the dependencies:
```bash
git clone https://github.com/alfredpanakkal/NAVAREA-1.git
cd NAVAREA-1

pip install -e .[all]
pip install requests supabase
```

### 2. Manual Pipeline Run
Run the pipeline stages sequentially:
```bash
# Step 1: Scrape verbatim warnings
python navarea_scraper.py

# Step 2: Parse, normalize coordinates & generate GeoJSON
python navarea_parser.py

# Step 3: Upsert into Supabase (requires environment variables)
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-or-service-key"
python supabase_sync.py
```

### 3. Automated Cloud Pipeline (GitHub Actions)
Continuous integration and recurring synchronization are handled via `.github/workflows/navarea-test.yml`:
- **Triggers:** Push to `main`, scheduled cron intervals (every 6 hours), or manual trigger (`workflow_dispatch`).
- **Secrets Required:**
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
- Runs in a clean Ubuntu runner, verifies scraping and parsing integrity, and publishes live updates to [Helm.Warning](https://helmwarning.vercel.app/).

---

## 📜 Acknowledgments & Credits

**Scrapling Framework**  
This repository originated as a fork of [Scrapling](https://github.com/D4Vinci/Scrapling), an adaptive web scraping framework. All credit for the underlying scraping framework, fetcher engines, and DOM selectors goes to the original creator **Karim Shoair (D4Vinci)** and the contributors to the Scrapling project.

* [Scrapling GitHub Repository](https://github.com/D4Vinci/Scrapling)
* [Scrapling Documentation](https://scrapling.readthedocs.io)
