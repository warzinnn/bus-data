# Project setup: 
This page contains some information about the project setup.

### Project requirements
```
# In a virtual env.
pip3 install -r requirements.txt
```

### GCP Account
Setup a Google Cloud account. (In my case i used the free trial account)
- Also generate an Google Application Credentials (JSON) over IAM -> Account Service menu.
- Apply account permissions over BigQuery, Storage and Compute Engine. (Also over IAM menu)

### Terraform
- Update the values of variables according to your project/google cloud information over `terraform/variables.tf` file.

### Sptrans API KEY
Generate an developer SPTRANS API Key over [Sptrans-Site](https://www.sptrans.com.br/desenvolvedores)

### Configuring `.env` file
The `.env` file should be in the root folder and needs to contain the following environments:
`SPTRANS_API_KEY=<KEY>`
`GOOGLE_APPLICATION_CREDENTIALS=/opt/workspace/.google/<YOUR_JSON_FILE>`

Add the google credentials json file in two locations:
1) Inside `src/.google` folder (This folder will be mapped with VM).
2) Inside the `airflow/data/.google` folder.(It will be used by airflow application).  

Example:  
`src/.google/<YOUR_JSON_FILE>`   
`airflow/data/.google/<YOUR_JSON_FILE>`

### Folder permissions
- Give airflow folder permission to avoid errors.
```
cd <ROOT_PROJECT_FOLDER>
sudo chmod -R u=rwx,g=rwx,o=rwx airflow/
```

### Building docker images

1) Build spark and airflow images
```
cd docker
chmod +x build_images.sh
./build_images.sh
```

2) Configure airflow
```
cd ../airflow
docker-compose up airflow-init
```

### Running docker images
```
cd ../docker
chmod +x manage_docker.sh
./manage_docker.sh --up

cd ../airflow
docker-compose up -d
```

### Configuring kafka

1) Create kafka topic
```
# In the root path of project
python3 src/admin_kafka.py 
```

2) Running kafka producer
```
# In the root path of project
python3 run.py
```

3) Running consumer
- First update the google cloud variables in `src/consumer.py` according to your project information.
    - The variables are: `BUCKET_NAME` and `CREDENTIALS_PATH`
- Run the following command:
```
docker exec -it spark-master /opt/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.apache.spark:spark-avro_2.12:3.4.0,org.apache.spark:spark-streaming-kafka-0-10_2.12:3.4.0 --master spark://spark-master:7077 /opt/workspace/consumer.py --topic running-buses
```

### DBT profile
- Setup a dbt profile in `profiles.yml` in the folder `airflow/data/dbt_bus_data/profiles.yml` as mentioned in the [dbt docs](https://docs.getdbt.com/docs/core/connect-data-platform/connection-profiles#setting-up-your-profile)
- Also this profile should contain information about the google cloud account.

### Airflow
First create the bigquery connection under connections menu. `Menu -> Admin -> Connections`. After that its possible to run the dags.

<img width="600" alt="connection_config" src="https://github.com/warzinnn/bus-data/assets/102708101/7bfcd7c7-f7e7-45e3-8a06-baa948ae74eb">

In the airflow there are 4 dags.
- **running-buses-dag-controller** is responsible to coordenates all the others.
- **running-buses-clean-files-dag** is responsible to clean invalid file in the data lake.
- **running-buses-dbt-dag** is responsible to run the DBT.
- **running-buses-gcs-files-dag** is responsible to create the external table in bigquery.

<img width="600" alt="airflow_dags" src="https://github.com/warzinnn/bus-data/assets/102708101/bfe1b40f-9164-4bc7-b2ab-48220a810624">