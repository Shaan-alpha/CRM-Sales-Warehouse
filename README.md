# CRM + Sales Warehouse

End-to-end data engineering project on the **Maven Analytics CRM + Sales** dataset. Raw operational CSVs are extracted, cleaned, loaded into a containerised Postgres warehouse, modelled into a star schema, validated with SQL data-quality checks, and surfaced through a five-page Power BI executive dashboard.

**Stack (all free):** Python 3.11 · pandas · PostgreSQL 16 (Docker) · pyarrow · Power BI Desktop

## Status

**✅ Complete.** Pipeline runs end-to-end and the dashboard ships in [`powerbi/powerbicrm_dashboard.pbix`](powerbi/powerbicrm_dashboard.pbix).

## Dashboard

A five-page executive dashboard built on the warehouse star schema.

### 1. Executive Overview

Won revenue, win rate, average deal size, and at-risk pipeline at a glance. Monthly trend and full pipeline funnel side by side.

![Executive Overview](docs/screenshots/01-executive-overview.png)

### 2. Agent Performance

How 30 agents and 6 managers drive the revenue. Win-rate × deal-size archetypes, manager-level revenue per agent, and a sortable agent leaderboard.

![Agent Performance](docs/screenshots/02-agent-performance.png)

### 3. Pipeline Analysis

Where the pipeline gets stuck and how to unstick it. Stalled-deal histogram, stage-to-stage funnel, and an interactive recovery-rate slider that projects revenue impact in real time.

![Pipeline Analysis](docs/screenshots/03-pipeline-analysis.png)

### 4. Product Deep Dive

Volume vs. value — why product strategy isn't about deal counts. Scatter of won-deals × avg deal size, sector × product revenue heatmap, and a velocity table ranking products by revenue per active day.

![Product Deep Dive](docs/screenshots/04-product-deep-dive.png)

### 5. Regional Analysis

Three regions, three playbooks. Geographic revenue map, sector × region stacked bars, and a regional comparison table covering agents, opportunities, win rate, deal size, and revenue per agent.

![Regional Analysis](docs/screenshots/05-regional-analysis.png)

### Data Model

Star schema directly from the warehouse (`dw.*` schema in Postgres) — five dimensions and one fact, plus calculation groups (`_Measures`), recovery-rate parameter, and a `RegionGeo` lookup for the map.

![Data Model](docs/screenshots/06-data-model.png)

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
Power BI Desktop  →  powerbi/powerbicrm_dashboard.pbix
```

Orchestration is a single Python entry point — [`etl/run_pipeline.py`](etl/run_pipeline.py) — which runs every stage in order and halts immediately if any stage fails, so bad data never reaches the warehouse.

## Star schema

| Layer | Tables |
| --- | --- |
| **Staging** (`stg.*`) | `accounts`, `products`, `sales_pipeline`, `sales_teams` — typed, deduped Parquet → Postgres |
| **Warehouse** (`dw.*`) | `dim_date`, `dim_account`, `dim_product`, `dim_sales_agent`, `fact_sales`, plus `RegionGeo` lookup |

Surrogate keys on every dim, conformed `date_key` across the model, fact grain = one row per opportunity in the sales pipeline.

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
├── powerbi/
│   └── powerbicrm_dashboard.pbix   # final 5-page Power BI report
├── data/
│   ├── raw/                    # input CSVs (gitignored)
│   ├── staging/                # parquet snapshots (gitignored)
│   └── archive/                # historical pipeline runs (gitignored)
├── docs/
│   ├── data_dictionary.csv     # column-level definitions
│   ├── roadmap.md              # build journal
│   └── screenshots/            # dashboard screenshots used in this README
├── docker-compose.yml          # Postgres 16 + pgAdmin
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

Open [`powerbi/powerbicrm_dashboard.pbix`](powerbi/powerbicrm_dashboard.pbix) in Power BI Desktop. Refresh the data source to point at your local Postgres (`dw` schema).

## Data-quality checks

Every pipeline run validates:

- **Row counts** — staging vs. warehouse parity per source table
- **Null discipline** — no nulls on primary-key columns or required dimension attributes
- **Referential integrity** — every fact row resolves to a valid dim
- **Freshness** — most-recent `close_date` in `fact_sales` is within an expected window
- **Domain checks** — sector spelling normalised (`technolgy` → `technology`), deal stages limited to the known enum (Won / Lost / Engaging / Prospecting)

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
