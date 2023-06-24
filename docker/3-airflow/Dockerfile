FROM apache/airflow:latest-python3.11

USER root
RUN sudo apt update -y && apt install -y libgeos-dev

USER airflow
COPY requirements.txt .
RUN pip3 install -r requirements.txt