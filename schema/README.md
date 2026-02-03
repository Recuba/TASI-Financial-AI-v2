# TASI Financial Database Schema

PostgreSQL + pgvector database schema optimized for Vanna AI natural language queries.

## Schema Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    sectors      │     │   companies     │     │ fiscal_periods  │
│─────────────────│     │─────────────────│     │─────────────────│
│ sector_id (PK)  │◄────│ sector_id (FK)  │     │ period_id (PK)  │
│ sector_name     │     │ ticker          │     │ fiscal_year     │
│ embedding       │     │ company_name    │     │ fiscal_quarter  │
└─────────────────┘     │ embedding       │     │ period_type     │
                        └────────┬────────┘     └────────┬────────┘
                                 │                       │
                                 ▼                       ▼
                        ┌────────────────────────────────┐
                        │     financial_statements       │
                        │────────────────────────────────│
                        │ statement_id (PK)              │
                        │ company_id (FK)                │
                        │ period_id (FK)                 │
                        │ revenue, net_profit, etc.      │
                        └────────────────┬───────────────┘
                                         │
                                         ▼
                        ┌────────────────────────────────┐
                        │      financial_metrics         │
                        │────────────────────────────────│
                        │ statement_id (FK)              │
                        │ ROE, ROA, margins, ratios      │
                        │ profit_status, roe_status      │
                        └────────────────────────────────┘
                                         │
                                         ▼
                        ╔════════════════════════════════╗
                        ║    company_financials (VIEW)   ║
                        ║────────────────────────────────║
                        ║ Denormalized for easy querying ║
                        ║ Values in MILLIONS SAR         ║
                        ║ Ratios as PERCENTAGES          ║
                        ╚════════════════════════════════╝
```

## Quick Start

### 1. Prerequisites

```bash
# PostgreSQL 15+ with pgvector extension
sudo apt install postgresql-15-pgvector  # Ubuntu
brew install pgvector                     # macOS
```

### 2. Create Database

```bash
createdb tasi_financials
psql tasi_financials -c "CREATE EXTENSION vector;"
psql tasi_financials -c "CREATE EXTENSION pg_trgm;"
```

### 3. Apply Schema

```bash
psql tasi_financials -f 01_schema.sql
```

### 4. Migrate Data

```bash
# Set your database URL
export DATABASE_URL="postgresql://user:password@localhost:5432/tasi_financials"

# Run migration
pip install pandas psycopg2-binary
python 02_etl_migrate.py
```

### 5. Train Vanna AI

```bash
export VANNA_API_KEY="your-api-key"
pip install vanna
python 03_vanna_training.py
```

## Key Design Decisions

### Normalization

| Original CSV | Normalized Schema |
|--------------|-------------------|
| 91 columns | 5 tables |
| Company info repeated | `companies` dimension table |
| Period info repeated | `fiscal_periods` dimension table |
| Redundant ratio formats | Single canonical value |

### Data Types

| Field Type | Choice | Rationale |
|------------|--------|-----------|
| Money | `NUMERIC(20,2)` | Exact precision, SAR values |
| Ratios | `NUMERIC(10,6)` | Decimal format (0.15 = 15%) |
| Dates | `DATE` | Proper date operations |
| Text | `VARCHAR(n)` | Sized appropriately |

### Indexes

| Index | Purpose |
|-------|---------|
| `companies(ticker)` | Company lookups |
| `financial_statements(company_id, period_id)` | Time series queries |
| `financial_statements(is_latest)` | Latest data filter |
| `financial_metrics(return_on_equity)` | Profitability ranking |
| `companies(embedding)` | Semantic search (pgvector) |

## Vanna AI Usage

### Materialized View

The `company_financials` view is optimized for natural language queries:

```sql
-- Values are human-readable
SELECT ticker, company_name,
       revenue_millions,      -- In millions SAR (not raw SAR)
       roe_percent            -- As percentage (15, not 0.15)
FROM company_financials
WHERE is_latest = TRUE;
```

### Semantic Search

Find companies using natural language:

```python
# Search by description similarity
results = vn.ask("Find companies similar to Saudi Aramco")

# The schema supports pgvector embeddings for semantic search
```

### Example Queries

```sql
-- "Show me profitable companies"
SELECT * FROM company_financials
WHERE profit_status = 'Profit' AND is_latest = TRUE;

-- "Companies with excellent ROE"
SELECT * FROM company_financials
WHERE roe_status = 'Excellent' AND is_latest = TRUE;

-- "Top 10 by revenue in 2024"
SELECT * FROM company_financials
WHERE fiscal_year = 2024 AND is_annual = TRUE
ORDER BY revenue_millions DESC
LIMIT 10;
```

## Maintenance

### Refresh Materialized View

After data updates:

```sql
REFRESH MATERIALIZED VIEW company_financials;
```

### Update Embeddings

After adding new companies:

```python
# Generate embeddings for new companies
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=company_description
)
embedding = response.data[0].embedding

# Update in database
cursor.execute("""
    UPDATE companies SET embedding = %s WHERE company_id = %s
""", (embedding, company_id))
```

## Files

| File | Purpose |
|------|---------|
| `01_schema.sql` | Database schema DDL |
| `02_etl_migrate.py` | CSV to PostgreSQL migration |
| `03_vanna_training.py` | Vanna AI training script |
| `04_sample_queries.sql` | Test queries |

## Removed Redundant Columns

The following redundant columns from the CSV were normalized:

- `calc_ROE`, `calc_ROA`, etc. → Stored once in `financial_metrics`
- `roe_pct`, `roe_decimal` → Single `return_on_equity` (decimal)
- `revenue_millions` → Calculated in view from `revenue`
- `period_label` → Generated from `fiscal_year` + `fiscal_quarter`
- `ticker_name` → Join `companies.ticker` + `companies.company_name`
