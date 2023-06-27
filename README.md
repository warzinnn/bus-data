# SP Bus Data - DE Project

A data pipeline using a streaming dataset from SPTRANS API which is a company that manages the bus transportation system in some regions of São Paulo, Brazil. This project was realized for studies purposes.

### Overview
In this project, the creation and management of cloud resources (Google Cloud) was done with Terraform. The workflow orchestration was managed by Airflow, which coordenates the integration with GCS (data lake), DBT (data transformation) and BigQuery (data warehouse). The kafka, spark and airflow instances was containerized with docker and hosted in Google Compute Engine. The final data is served on Looker Studio.

The Kafka producer will stream events generated from SPTRANS API every two minutes to the target topics, and the pyspark will handle the stream processing of real-time data. The processed data will be stored in data lake periodically (also every two minutes). From that, the DAGs from airflow will be triggered every three minutes to run the creation of tables in bigquery and do the data transformation with DBT, so, in the end the data will be available in Looker Studio for visualization.

### Pipeline Flow
<img width="1179" alt="pipeline_flow" src="https://github.com/warzinnn/bus-data/assets/102708101/71ce756c-cdec-42d3-ac7e-0e71897cca22">

### Looker Studio Visualization
<img width="1020" alt="data_visualization" src="https://github.com/warzinnn/bus-data/assets/102708101/8838e4e4-832b-4d12-b3c6-ed198f05b862">

### Documentation
- [**Config & Installation**](documentation.md)

### Tools and Technologies Used
- [**Python**](https://www.python.org)
- Stream Processing:
    - [**Kafka**](https://kafka.apache.org/)
    - [**Spark Structured Streaming**](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [**GCP - Google Cloud Platform**](https://cloud.google.com)
    - Infrastructure as Code software (IaC): [**Terraform**](https://www.terraform.io)
    - Data Lake: [**Google Cloud Storage**](https://cloud.google.com/storage)
    - Data Warehouse: [**BigQuery**](https://cloud.google.com/bigquery)
    - [**Google Compute Engine**](https://cloud.google.com/compute?hl=pt-br)
- Containerization: [**Docker**](https://www.docker.com)
- Workflow Orchestration: [**Apache Airflow**](https://airflow.apache.org/)
- Data Transformation: [**dbt**](https://www.getdbt.com)
- Data Visualization - [**Looker Studio**](https://lookerstudio.google.com/)
