import pendulum
from airflow_dbt.operators.dbt_operator import DbtRunOperator

from airflow import DAG

with DAG(
    dag_id="running-buses-dbt-dag",
    description="DBT RUN",
    start_date=pendulum.now(),
    tags=["live-buses"],
) as dag:
    dbt_test = DbtRunOperator(
        task_id="dbt_run",
        select="stg_running_buses",
        profiles_dir="/opt/airflow/tmp_data/dbt_bus_data/.dbt_profile",
        dir="/opt/airflow/tmp_data/dbt_bus_data",
    )
