FROM cluster-base

RUN curl https://dlcdn.apache.org/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz -o spark-3.4.0-bin-hadoop3.tgz && \
    mkdir -p /opt/spark && \
    tar zxvf spark-3.4.0-bin-hadoop3.tgz -C /opt/spark --strip-components=1 && \
    rm spark-3.4.0-bin-hadoop3.tgz && \
    echo 'export SPARK_HOME="/opt/spark"' >> ~/.bashrc && \
    echo 'export PATH="${SPARK_HOME}/bin:${PATH}"' >> ~/.bashrc && \
    mkdir /opt/spark/logs && \
    touch /opt/spark/logs/spark-master.out && \
    touch /opt/spark/logs/spark-worker.out && \
    ln -sf /dev/stdout $SPARK_MASTER_LOG && \
    ln -sf /dev/stdout $SPARK_WORKER_LOG

ENV JAVA_HOME="/opt/java/jdk-11.0.2" \ 
    SPARK_HOME=/opt/spark \
    SPARK_MASTER_HOST=spark-master \
    SPARK_MASTER_PORT=7077 \
    SPARK_MASTER="spark://spark-master:7077" \
    SPARK_MASTER_WEBUI_PORT=8080 \
    SPARK_LOG_DIR=/opt/spark/logs \
    SPARK_MASTER_LOG=/opt/spark/logs/spark-master.out \
    SPARK_WORKER_LOG=/opt/spark/logs/spark-worker.out \
    SPARK_WORKER_WEBUI_PORT=8080 \
    PYSPARK_PYTHON=python3 

COPY jars/gcs-connector-hadoop3-latest.jar /opt/spark/jars

WORKDIR /opt/spark