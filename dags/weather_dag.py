from __future__ import annotations
import json
from datetime import datetime, timedelta
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from etl.extract import extract_all_cities
from etl.transform import transform_all
from etl.load import load_to_postgres
from io import StringIO


# Default settings shared by every task
DEFAULT_ARGS = {
    "owner":           "data_engineer",
    "retries":         1,
    "retry_delay":     timedelta(minutes=5),
    "email_on_failure": False,
}


def run_extract(**context):
    """Task 1: fetch data and push raw JSON to XCom."""
  
    raw = extract_all_cities()
    # Push to XCom as JSON string (XCom values must be serialisable)
    context["ti"].xcom_push(key="raw_data", value=json.dumps(raw))


def run_transform(**context):
    """Task 2: pull raw JSON from XCom, clean it, push CSV to XCom."""
    
    # Pull raw data that run_extract pushed
    raw_json = context["ti"].xcom_pull(
        task_ids="extract_task", key="raw_data"
    )
    raw = json.loads(raw_json)
    clean_df = transform_all(raw)
    # DataFrames aren't JSON-serialisable, so we convert to CSV first
    context["ti"].xcom_push(
        key="clean_csv", value=clean_df.to_csv(index=False)
    )


def run_load(**context):
    """Task 3: pull CSV from XCom and load into PostgreSQL."""

    clean_csv = context["ti"].xcom_pull(
        task_ids="transform_task", key="clean_csv"
    )
    # Rebuild the DataFrame from the CSV string
    df = pd.read_csv(StringIO(clean_csv), parse_dates=["forecast_date"])
    load_to_postgres(df)


# ── Register the DAG with Airflow ──────────────────────────────────
with DAG(
    dag_id="uk_weather_etl_pipeline",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule="0 7 * * *",  # Run at 07:00 every day
    catchup=False,
    tags=["weather", "etl", "portfolio"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_task", python_callable=run_extract
    )
    transform_task = PythonOperator(
        task_id="transform_task", python_callable=run_transform
    )
    load_task = PythonOperator(
        task_id="load_task", python_callable=run_load
    )

    # >> means "run this before that"
    extract_task >> transform_task >> load_task