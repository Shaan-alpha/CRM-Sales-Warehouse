from datetime import datetime
from pathlib import Path
from etl.extract import main as extract_main
from etl.load_staging import main as load_main
from etl.transform_warehouse import main as transform_main
from etl.quality_checks import main as quality_main

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

PROJECT_ROOT = Path("/usr/local/airflow")

with DAG(
    dag_id="crm_sales_warehouse_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="0 0 * * *",
    catchup=False,
    tags=["crm", "etl", "warehouse"],
) as dag:
    extract_data = PythonOperator(
    task_id="extract_data",
    python_callable=extract_main,
)

load_staging = PythonOperator(
    task_id="load_staging",
    python_callable=load_main,
)

transform_warehouse = PythonOperator(
    task_id="transform_warehouse",
    python_callable=transform_main,
)

quality_checks = PythonOperator(
    task_id="quality_checks",
    python_callable=quality_main,
)

extract_data >> load_staging >> transform_warehouse >> quality_checks
