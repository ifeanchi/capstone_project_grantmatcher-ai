# GrantMatcher AI — Capstone Project

> An intelligent grant discovery system that combines semantic search with LLM reasoning to help nonprofits and researchers find relevant funding opportunities faster.

---

## Problem Statement

Nonprofit teams and researchers waste 10–20 hours/week manually searching for grants. Keyword-based tools miss relevant opportunities due to terminology gaps, leading to missed funding and inefficient resource allocation.

---

## Why It Matters

- Increases funding success rates for mission-driven organizations
- Demonstrates responsible AI: transparent matching, human-in-the-loop design
- Showcases production-ready RAG architecture using open-source tools

---

## Architecture Overview

This project uses a **two-database hybrid architecture** based on professor feedback:

| Layer | Technology | Purpose |
|-------|------------|---------|
| Structured Grant Storage | **SQLite** | Store, update, and query grant records (title, deadline, amount, field, eligibility) |
| Semantic Search | **ChromaDB** | Vector embeddings for similarity-based matching |
| LLM Reasoning | **Llama 3 (8B) via Ollama** | Generate fit rationale for matched grants |
| Orchestration | **LangChain** | Chains, prompt templates, retrieval pipeline |
| Embeddings | **Sentence-Transformers** (`all-MiniLM-L6-v2`) | Convert text to vector representations |
| UI | **Streamlit** | Lightweight user interface |

---

## Tools & Frameworks

- **LLM:** Llama 3 (8B) via Ollama (local execution)
- **Orchestration:** LangChain (chains, prompt templates)
- **Structured DB:** SQLite (grant catalog, updatable records)
- **Vector DB:** ChromaDB (semantic search + metadata filtering)
- **Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`)
- **UI:** Streamlit
- **Data Sources:** Grants.gov API, NSF Awards API, NIH RePORTER API, curated manual entries

---

## Grant Data Sources

The system ingests grant data from **three free public APIs** — no subscriptions or API keys required for the core endpoints — plus a curated manual entry path for private foundation grants.

### Grants.gov *(Primary Source)*

The U.S. government's central grants portal. Offers two RESTful endpoints with no authentication required:

- **`search2`** — search opportunities by keyword, agency, category, deadline, and status
- **`fetchOpportunity`** — retrieve full details for a specific grant (eligibility, award range, synopsis)

```python
import requests

def fetch_grants_gov(keyword, max_results=25):
    url = "https://apply07.grants.gov/grantsws/rest/opportunities/search/"
    payload = {
        "keyword": keyword,
        "rows": max_results,
        "oppStatuses": "posted"
    }
    response = requests.post(url, json=payload)
    return response.json().get("oppHits", [])
```

**Docs:** https://grants.gov/api/api-guide

---

### NSF Awards API *(Research Grants)*

The National Science Foundation's public API. No authentication required. Supports filtering by keyword, institution, PI name, award ID, and date range.

```python
def fetch_nsf_awards(keyword, max_results=25):
    url = "http://api.nsf.gov/services/v1/awards.json"
    params = {
        "keyword": keyword,
        "rpp": max_results,
        "printFields": "title,abstractText,fundsObligated,expDate,agency"
    }
    response = requests.get(url, params=params)
    return response.json().get("response", {}).get("award", [])
```

**Docs:** https://resources.research.gov/common/webapi/awardapisearch-v1.htm

---

### NIH RePORTER API *(Health & Biomedical)*

The National Institutes of Health's public project database. No authentication required. Returns abstracts, funding amounts, PI names, and award details.

```python
def fetch_nih_grants(keyword, fiscal_year=2025):
    url = "https://api.reporter.nih.gov/v2/projects/search"
    payload = {
        "criteria": {
            "advanced_text_search": {
                "operator": "and",
                "search_field": "all",
                "search_text": keyword
            },
            "fiscal_years": [fiscal_year]
        },
        "limit": 25
    }
    response = requests.post(url, json=payload)
    return response.json().get("results", [])
```

**Docs:** https://api.reporter.nih.gov

---

### Private Foundation Grants *(Manual Entry)*

Grants from private foundations (Ford Foundation, Gates Foundation, etc.) have **no public API**. These are added manually as curated entries directly into SQLite using the `update_grants.py` script, or loaded from a JSON file.

```bash
python db/update_grants.py --add "data/foundation_grants.json"
```

---

### API vs. Manual Entry Summary

| Source | API Available | Auth Required | Best For |
|--------|:------------:|:-------------:|----------|
| Grants.gov | ✅ | ❌ | Nonprofits, federal programs |
| NSF Awards | ✅ | ❌ | Research, STEM, universities |
| NIH RePORTER | ✅ | ❌ | Health, biomedical research |
| Private Foundations | ❌ | — | Manual / curated entry |

---

## Database Design

### SQLite — Grant Catalog (`grants.db`)

SQLite is the **source of truth** for all grant records. It stores structured metadata that is easy to update, query, and filter. As new grants are pulled from APIs or added manually, the database is updated here first, then synced to ChromaDB.

```sql
CREATE TABLE grants (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    organization     TEXT,
    field            TEXT,
    source           TEXT,           -- e.g. 'grants.gov', 'nsf', 'nih', 'manual'
    deadline         DATE,
    min_amount       INTEGER,
    max_amount       INTEGER,
    eligibility      TEXT,
    description      TEXT,
    url              TEXT,
    chroma_synced_at TIMESTAMP,      -- tracks embedding sync state
    last_updated     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(title, organization)      -- prevents duplicate entries
);
```

**Update workflow:** Fetch from API → upsert into SQLite → re-embed new/changed descriptions → sync to ChromaDB.

### ChromaDB — Vector Store

ChromaDB stores **embeddings of grant descriptions** for semantic search. It is populated from SQLite and refreshed whenever new or updated records are detected via the `chroma_synced_at` timestamp.

```
Grants.gov API ──┐
NSF API         ──┼──▶  SQLite (grants.db)  ──▶  ChromaDB (vectors)
NIH API         ──┤         source of truth          semantic index
Manual Entry    ──┘              │
                                 ▼
                         LLM Reasoning (Llama 3)
                                 │
                                 ▼
                        Streamlit UI (results)
```

---

## Updating the Grant Catalog

### Pull from APIs

```bash
# Fetch new grants by keyword and upsert into SQLite
python db/update_grants.py --source grants_gov --keyword "nonprofit education"
python db/update_grants.py --source nsf --keyword "community health"
python db/update_grants.py --source nih --keyword "mental health services"
```

### Add Manual / Foundation Grants

```bash
python db/update_grants.py --add "data/foundation_grants.json"
```

### Sync to ChromaDB

After updating SQLite, re-embed any records where `chroma_synced_at` is null or older than `last_updated`:

```bash
python db/sync_chroma.py
```

This will:
1. Query SQLite for records that need (re-)embedding
2. Generate embeddings via Sentence-Transformers
3. Upsert vectors into ChromaDB
4. Update `chroma_synced_at` on each synced record

### Filter Expired Grants

```sql
-- Only surface active grants in search
SELECT * FROM grants WHERE deadline >= DATE('now');
```

---

## Expected Workflow

1. User pastes a project description and applies optional filters (field, deadline, funding range)
2. Input is embedded using Sentence-Transformers
3. ChromaDB performs semantic similarity search and returns top candidates
4. SQLite is queried to retrieve full structured metadata for those candidates
5. Top-3 results are passed to Llama 3 with a structured prompt to generate fit rationale
6. Streamlit displays matches with relevance scores, reasons, deadlines, and responsible-AI disclaimers

---

## Project Structure

```
grantmatcher-ai/
│
├── data/
│   ├── foundation_grants.json   # Curated private foundation grants
│   └── grants.db                # SQLite database (auto-generated)
│
├── db/
│   ├── seed_sqlite.py           # Initial load from JSON → SQLite
│   ├── sync_chroma.py           # SQLite → ChromaDB embeddings
│   └── update_grants.py         # Fetch from APIs + manual add + re-sync
│
├── ingestion/
│   ├── grants_gov.py            # Grants.gov API client
│   ├── nsf.py                   # NSF Awards API client
│   └── nih.py                   # NIH RePORTER API client
│
├── retrieval/
│   ├── semantic_search.py       # ChromaDB query logic
│   └── metadata_filter.py       # SQLite filter queries
│
├── llm/
│   ├── chain.py                 # LangChain pipeline
│   └── prompts.py               # Prompt templates
│
├── app.py                       # Streamlit UI entry point
├── requirements.txt
└── README.md
```

---

## Setup & Installation

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/grantmatcher-ai.git
cd grantmatcher-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pull the Llama 3 model via Ollama
ollama pull llama3

# 4. Seed the SQLite database with initial data
python db/seed_sqlite.py

# 5. (Optional) Pull live grants from APIs
python db/update_grants.py --source grants_gov --keyword "nonprofit"
python db/update_grants.py --source nsf --keyword "research"

# 6. Sync embeddings to ChromaDB
python db/sync_chroma.py

# 7. Launch the app
streamlit run app.py
```

---

## Responsible AI Design

- **Transparency:** All matches include a relevance score and LLM-generated rationale
- **Human-in-the-loop:** Users are encouraged to verify deadlines and eligibility directly with grant organizations
- **Disclaimer:** Results are AI-assisted suggestions, not guarantees of eligibility
- **Local execution:** All LLM inference runs locally via Ollama — no data sent to external APIs
- **Source attribution:** Every grant record tracks its origin (`source` column) for auditability

---

## Success Metrics

- ✅ Application runs end-to-end with real or mock data
- ✅ SQLite database is queryable and updatable without restarting the app
- ✅ At least one live API (Grants.gov, NSF, or NIH) successfully populates the database
- ✅ Semantic search returns contextually relevant grants (not just keyword matches)
- ✅ LLM produces coherent, structured fit rationale for each match
- ✅ UI clearly communicates match scores, deadlines, and AI limitations
- ✅ Clear documentation + workflow diagram + 5-min presentation

---

## Additional Suggestions

### 1. Scheduled API Refresh
Set up a cron job or Streamlit background task to automatically re-pull from Grants.gov, NSF, and NIH on a weekly cadence so the database stays current without manual intervention.

### 2. Relevance Feedback Loop
Allow users to mark matches as "relevant" or "not relevant." Store this feedback in a `feedback` table in SQLite to re-rank results over time.

### 3. Export to CSV / PDF
Add a Streamlit button to export matched grants to a shareable report — useful for handing off results to a program director or grant writer.

### 4. Embedding Model Versioning
If you upgrade the embedding model, all descriptions need to be re-embedded. The `chroma_synced_at` column in SQLite makes it easy to detect stale records and re-sync only what changed.

### 5. Multi-query Expansion
Use LangChain's `MultiQueryRetriever` to generate 3 variations of the user's input and merge the results — this improves recall when the user's phrasing differs from grant language.

### 6. Field / Category Taxonomy
Define a controlled vocabulary for the `field` column (e.g., Education, Health, Environment, Arts) so filters in the Streamlit UI are consistent and reliable across all data sources.

### 7. Deadline Alerts
Add a simple check that flags grants expiring within the next 14 days and surfaces them as a priority section in the UI.

---

## License

MIT License — see `LICENSE` for details.
