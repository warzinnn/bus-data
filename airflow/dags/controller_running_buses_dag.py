import pendulum
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from airflow import DAG

"""
    Dag used as controller using the operator TriggerDagRunOperator.
    It triggers every 3 minutes the dag `trigger_gcp_dag` and then `trigger_dbt_dag` .
"""
# schedule="*/3 * * * *"
# @once
with DAG(
    dag_id="running-buses-dag-controller",
    start_date=pendulum.now().subtract(minutes=3),
    catchup=False,
    schedule="*/3 * * * *",
    tags=["live-buses"],
) as dag:
    trigger_gcp_dag = TriggerDagRunOperator(
        task_id="trigger-running-buses-gcp-dag",
        trigger_dag_id="running-buses-gcs-files-dag",
    )

    trigger_dbt_dag = TriggerDagRunOperator(
        task_id="trigger-running-buses-dbt-dag",
        trigger_dag_id="running-buses-dbt-dag",
    )

    trigger_clean_files_dag = TriggerDagRunOperator(
        task_id="trigger-running-buses-clean-files-dag",
        trigger_dag_id="running-buses-clean-files-dag",
    )

    trigger_gcp_dag >> trigger_dbt_dag >> trigger_clean_files_dag
