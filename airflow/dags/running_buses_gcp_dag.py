import pendulum
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateExternalTableOperator,
    BigQueryDeleteTableOperator,
)

from airflow import DAG

with DAG(
    dag_id="running-buses-gcs-files-dag",
    description="GCP MANAGER DAG",
    start_date=pendulum.now(),
    tags=["live-buses"],
) as dag:
    date = pendulum.now(tz="America/Sao_Paulo")
    day = date.format("DD")
    month = date.format("MM")
    year = date.format("YYYY")
    hour = date.format("HH")

    project_id = "bus-data-389717"
    bq_dataset_name = "dbt_busdata_stag"

    delete_table = BigQueryDeleteTableOperator(
        task_id="delete_table_running_buses",
        deletion_dataset_table=f"{project_id}.{bq_dataset_name}.external_table_running_buses",
        gcp_conn_id="google_cloud_default",
        ignore_if_missing=True,
    )

    gcs_bucket_name = "data_lake_bus_data_bus-data-389717"
    gcs_path_name = (
        f"running_buses/year={year}/month={month}/day={day}/hour={hour}/*.csv"
    )
    # gcs_path_name = f"running_buses/year={year}/month={month}/day={day}/hour=14/*.csv"
    # gcs_path_name = f"running_buses/year={year}/month={month}/day=22/hour=13/part-00000-29e33fc5-b95e-4f0e-b351-1f131fa0eeac-c000.csv"
    create_external_table = BigQueryCreateExternalTableOperator(
        task_id="create_external_table_running_buses",
        destination_project_dataset_table=f"{bq_dataset_name}.external_table_running_buses",
        bucket=gcs_bucket_name,
        source_objects=[gcs_path_name],
        schema_fields=[
            {"name": "line_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "line_number", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "qtd_running_buses", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        gcp_conn_id="google_cloud_default",
    )

    delete_table >> create_external_table
