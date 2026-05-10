from datetime import datetime
from pathlib import Path

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

PROJECT_ROOT = Path("/usr/local/airflow")

with DAG(
    dag_id="crm_sales_warehouse_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="0 0 * * *",
    catchup=False,
    tags=["crm", "etl", "warehouse"],
) as dag:
    extract_data = BashOperator(
        task_id="extract_data",
        bash_command=f"cd {PROJECT_ROOT} && python -m etl.extract",
    )

    load_staging = BashOperator(
        task_id="load_staging",
        bash_command=f"cd {PROJECT_ROOT} && python -m etl.load_staging",
    )

    transform_warehouse = BashOperator(
        task_id="transform_warehouse",
        bash_command=f"cd {PROJECT_ROOT} && python -m etl.transform_warehouse",
    )

    quality_checks = BashOperator(
        task_id="quality_checks",
        bash_command=f"cd {PROJECT_ROOT} && python -m etl.quality_checks",
    )

    extract_data >> load_staging >> transform_warehouse >> quality_checks
