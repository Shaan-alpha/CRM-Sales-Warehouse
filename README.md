# CRM + Sales Warehouse

End-to-end data engineering project on the **Maven Analytics CRM + Sales** dataset. Raw operational CSVs are extracted, cleaned, loaded into a containerised Postgres warehouse, modelled into a star schema, validated with SQL data-quality checks, and surfaced through a Power BI dashboard.

**Stack (all free):** Python 3.11 · pandas · PostgreSQL 16 (Docker) · pyarrow · Power BI Desktop

## Status

**✅ Complete.** Pipeline runs end-to-end and the dashboard is published.

## Architecture

```
CSV (data/raw)
      │  extract.py
      ▼
Parquet snapshots (data/staging)
      │  load_staging.py
      ▼
Postgres · staging schema
      │  transform_warehouse.py  (SQL: dim_date, dimensions, fact_sales)
      ▼
Postgres · warehouse schema (star)
      │  quality_checks.py  (SQL row counts, null/PK/FK, freshness)
      ▼
Power BI Desktop  →  powerbicrm_dashboard.pbix
```

Orchestration is a single Python entry point — [`etl/run_pipeline.py`](etl/run_pipeline.py) — which runs every stage in order and halts immediately if any stage fails, so bad data never reaches the warehouse.

## Star schema

| Layer | Tables |
| --- | --- |
| **Staging** (`stg.*`) | `accounts`, `products`, `sales_pipeline`, `sales_teams` — typed, deduped Parquet → Postgres |
| **Warehouse** (`dw.*`) | `dim_date`, `dim_account`, `dim_product`, `dim_sales_team`, `fact_sales` |

Surrogate keys on every dim, conformed `date_key` across the model, fact grain = one row per closed deal.

## Project structure

```
crm-sales-warehouse/
├── etl/
│   ├── extract.py              # CSV → cleaned parquet snapshots
│   ├── load_staging.py         # parquet → Postgres staging
│   ├── transform_warehouse.py  # staging → star schema (executes sql/transformations/*.sql)
│   ├── quality_checks.py       # row counts, nulls, PK/FK, freshness
│   ├── run_pipeline.py         # orchestrator — runs all four stages
│   └── utils/
│       ├── db.py               # SQLAlchemy engine + Postgres connection helpers
│       └── logger.py
├── sql/
│   ├── ddl/                    # CREATE SCHEMA + tables (staging, warehouse)
│   ├── transformations/        # dim_date, dimensions, fact_sales
│   └── quality_checks/         # checks.sql
├── data/
│   ├── raw/                    # input CSVs (gitignored)
│   ├── staging/                # parquet snapshots (gitignored)
│   └── archive/                # historical pipeline runs (gitignored)
├── docs/
│   ├── data_dictionary.csv     # column-level definitions
│   └── roadmap.md              # build journal
├── docker-compose.yml          # Postgres 16 + pgAdmin
├── powerbicrm_dashboard.pbix   # final Power BI dashboard
├── requirements.txt
├── .env.example
└── README.md
```

## Data

Source: [Maven Analytics — CRM + Sales](https://mavenanalytics.io/data-playground)

Place these files in `data/raw/` (gitignored):
- `accounts.csv`
- `products.csv`
- `sales_pipeline.csv`
- `sales_teams.csv`

Column-level definitions live in [`docs/data_dictionary.csv`](docs/data_dictionary.csv).

## Run it locally

### 1. Start Postgres

```powershell
docker compose up -d
```

This brings up Postgres 16 on `localhost:5432` and pgAdmin on `localhost:5050`. Schemas `stg` and `dw` are created on first start via the DDL scripts in `sql/ddl/`.

### 2. Set up Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edit .env — set POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
```

### 3. Drop the CSVs

Place the four Maven Analytics CSVs in `data/raw/`.

### 4. Run the full pipeline

```powershell
python -m etl.run_pipeline
```

This runs **extract → load → transform → quality checks** sequentially. Any stage that fails halts the run with a non-zero exit code.

### 5. Open the dashboard

Open `powerbicrm_dashboard.pbix` in Power BI Desktop. Refresh the data source to point at your local Postgres (`dw` schema).

## What the dashboard shows

- Revenue and deal-count trends over time, by quarter and by sales agent
- Product-level performance (top sellers, conversion rates)
- Sector breakdown across accounts (technology, finance, retail, etc.)
- Sales-team leaderboards and regional performance
- Deal-stage funnel: prospecting → qualification → engaging → closed (won/lost)

## Data-quality checks

Every pipeline run validates:

- **Row counts** — staging vs. warehouse parity per source table
- **Null discipline** — no nulls on primary-key columns or required dimension attributes
- **Referential integrity** — every fact row resolves to a valid dim
- **Freshness** — most-recent `close_date` in `fact_sales` is within an expected window
- **Domain checks** — sector spelling normalised (`technolgy` → `technology`), deal stages limited to the known enum

A failed check halts the pipeline before the warehouse is updated.

## Tools used

| Layer | Tool |
| --- | --- |
| Source | Maven Analytics CRM + Sales (CSV) |
| Extract / load / transform | Python 3.11, pandas, pyarrow, SQLAlchemy |
| Database | PostgreSQL 16 (Docker) |
| Admin | pgAdmin 4 (Docker) |
| Quality | Plain SQL via `psycopg2` |
| Visualisation | Power BI Desktop |
| Container runtime | Docker Compose |

## License

[MIT](LICENSE)
