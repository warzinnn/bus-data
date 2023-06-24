import pendulum
from airflow.decorators import task

from airflow import DAG

with DAG(
    dag_id="running-buses-clean-files-dag",
    description="Dag to remove invalid files from data lake",
    start_date=pendulum.now(),
    tags=["live-buses"],
) as dag:

    @task.virtualenv(
        task_id="clean-gcp-files",
        requirements=["google-cloud-storage"],
        system_site_packages=True,
    )
    def clean_files():
        from airflow.hooks.base import BaseHook
        from google.cloud import storage

        bucket_name = "data_lake_bus_data_bus-data-389717"
        file_prefix = "running_buses/"

        conn = BaseHook.get_connection("google_cloud_default")
        creds = conn.get_extra().split('"')[3]

        storage_client = storage.Client.from_service_account_json(creds)
        blobs = storage_client.list_blobs(bucket_name, prefix=file_prefix)

        for blob in blobs:
            generation_match_precondition = blob.generation
            if blob.name.endswith(".csv") and blob.size == 0:
                print(f"removing invalid file: {blob.name}, blob size: {blob.size}")
                blob.delete(if_generation_match=generation_match_precondition)
                print(f"Blob {blob.name} deleted.")

    task = clean_files()
