# Build Roadmap

Build journal for the CRM + Sales Warehouse. Every stage shipped; the final deliverable is the five-page Power BI report at [`powerbi/powerbicrm_dashboard.pbix`](../powerbi/powerbicrm_dashboard.pbix).

## Stage 0 — Tools ✅
Installed Python 3.11, Docker Desktop, VS Code, Power BI Desktop, Git via winget.

## Stage 1 — Scaffold ✅
Repo structure, `.gitignore`, `.gitattributes`, virtualenv, VS Code config, requirements pinned.

## Stage 2 — Postgres in Docker ✅
`docker-compose.yml` brings up Postgres 16 + pgAdmin on a shared network. Two schemas (`stg`, `dw`) created on first start via the DDL scripts in `sql/ddl/`.

## Stage 3 — Extract ✅
[`etl/extract.py`](../etl/extract.py) parses the four Maven Analytics CSVs, normalises types, fixes the `technolgy → technology` typo, and writes immutable Parquet snapshots to `data/staging/` (gitignored).

## Stage 4 — Load staging ✅
[`etl/load_staging.py`](../etl/load_staging.py) loads the Parquet snapshots into the `stg` schema in Postgres using SQLAlchemy + `psycopg2`. Idempotent: drops and rebuilds staging tables on each run.

## Stage 5 — Transform → warehouse ✅
[`etl/transform_warehouse.py`](../etl/transform_warehouse.py) executes the SQL files in `sql/transformations/` in order:
- `01_dim_date.sql` — generated calendar dim with surrogate keys
- `02_dimensions.sql` — `dim_account`, `dim_product`, `dim_sales_agent` with surrogate keys
- `03_fact_sales.sql` — opportunity-grain fact, FKs into all four dims, conformed `date_key`s for engage/close

## Stage 6 — Quality checks ✅
[`etl/quality_checks.py`](../etl/quality_checks.py) runs `sql/quality_checks/checks.sql`:
- Row count parity between staging and warehouse
- Nulls on primary keys / required dim attributes
- Referential integrity (every fact row resolves to a dim)
- Freshness (most recent `close_date` within expected window)
- Domain checks (deal stage enum, sector spelling)

A failed check halts the pipeline before the warehouse is updated.

## Stage 7 — Power BI dashboard ✅
Five-page report on top of the warehouse:
1. **Executive Overview** — KPIs (Won Revenue, Win Rate, Avg Deal Size, Pipeline at Risk), monthly revenue trend, pipeline funnel
2. **Agent Performance** — agent archetypes scatter, manager performance, leaderboard
3. **Pipeline Analysis** — stalled-deals histogram, stage-to-stage funnel, recovery-rate parameter with revenue-impact projection
4. **Product Deep Dive** — volume × value scatter, sector × product heatmap, product velocity table
5. **Regional Analysis** — geographic map, sector × region bars, regional comparison table

Calculation groups (`_Measures`) and a what-if `Parameter` for the recovery-rate slider.

## Stage 8 — Orchestration (descoped from Airflow) ✅
Originally planned to use Airflow; for project scope a single Python orchestrator was sufficient. [`etl/run_pipeline.py`](../etl/run_pipeline.py) runs every stage in order and halts on any non-zero exit code. Easy to swap for an Airflow DAG later if needed.

## Stage 9 — Polish ✅
- README rewritten with architecture diagram, star schema, dashboard screenshots, run-it-locally steps
- Raw CSVs and `data/staging/` Parquet outputs gitignored
- Power BI file moved to dedicated `powerbi/` folder
- Empty scaffolding folders removed
- License added (MIT)
