import argparse
import json
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from google.cloud import storage
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SparkSession, types
from pyspark.sql.functions import (
    col,
    collect_list,
    count,
    current_timestamp,
    explode,
    from_json,
    from_utc_timestamp,
    udf,
    window,
)


def read_data_from_kafka(topic_name: str):
    """Read data from kafka topic"""
    df_stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "172.20.0.3:9092,broker:29092")
        .option("subscribe", topic_name)
        .option("startingOffsets", "latest")
        .option("checkpointLocation", "checkpoint")
        .load()
    )
    return df_stream


def sink_console(df, output_mode: str = "complete", processing_time: str = "1 minutes"):
    """Sink method for console output
    .foreachBatch(foreach_batch_function) # for 1 kafka

    """
    write_query = (
        df.writeStream.outputMode(output_mode)
        .format("console")
        .trigger(processingTime=processing_time)
        .option("truncate", False)
        .start()
    )
    return write_query


def sink_kafka_topic(df, topic_name, output_mode: str = "append"):
    """Sink method for kafka topic output"""
    write_query = (
        df.writeStream.format("kafka")
        .option("kafka.bootstrap.servers", "172.20.0.3:9092,broker:29092")
        .outputMode(output_mode)
        .option("topic", topic_name)
        .option("checkpointLocation", "checkpoint")
        .start()
    )
    return write_query


def sink_file(df, processing_time: str = "2 minute"):
    """Sink method for kafka file output

    date_time = datetime.now(ZoneInfo("America/Sao_Paulo"))
    date = date_time.strftime("%Y-%m-%d")
    time = date_time.strftime("%H")
    year = date.split("-")[0]
    month = date.split("-")[1]
    day = date.split("-")[2]
    .foreachBatch(foreach_batch_function_save_file)
            .option("coalesce", 1)
            .option("path", f"gs://data_lake_bus_data_bus-data-389717/year={year}/month={month}/day={day}/hour={time}")
        .option("mode", "append")
    """

    write_query = (
        df.writeStream.option("checkpointLocation", "asssdx/checkpoint")
        .trigger(processingTime=processing_time)
        .outputMode("update")
        .foreachBatch(foreach_batch_function_save_file)
        .start()
    )
    return write_query


def decode_data(data: any) -> str:
    """Method to convert data receveid from producer."""
    return str(json.loads(data.decode("utf-8")))


def foreach_batch_function(df, epoch_id):
    """Function to aggregates companies with the same id by the code area operation"""
    df = df.groupBy(
        "company_reference_code", "company_name", "total_stopped_buses", "timestamp"
    ).agg(collect_list("code_area_operation").alias("agg_code_area_operation"))

    df = df.select(
        "agg_code_area_operation",
        "company_reference_code",
        "company_name",
        "total_stopped_buses",
        "timestamp",
    )
    df.show(truncate=False)


def foreach_batch_function_save_file(df, epoch_id):
    """Function to aggregates companies with the same id by the code area operation"""
    date_time = datetime.now(ZoneInfo("America/Sao_Paulo"))
    date = date_time.strftime("%Y-%m-%d")
    time = date_time.strftime("%H")
    year = date.split("-")[0]
    month = date.split("-")[1]
    day = date.split("-")[2]
    file_name_time = date_time.strftime("%H:%M:%S")

    """df = df.groupBy(
        "company_reference_code", "company_name", "total_stopped_buses", "timestamp"
    ).agg(collect_list("code_area_operation").alias("agg_code_area_operation"))

    df = df.select(
        col("agg_code_area_operation").cast(types.StringType()),
        "company_reference_code",
        "company_name",
        "total_stopped_buses",
        "timestamp",
    )"""
    df = df.select(
        "code_area_operation",
        "company_reference_code",
        "company_name",
        "total_stopped_buses",
        "timestamp",
    )

    # .option("header","true") \
    df.repartition(1).write.mode("append").csv(
        f"gs://data_lake_bus_data_bus-data-389717/year={year}/month={month}/day={day}/hour={time}"
    )

    rename_file_bucket(year, month, day, time, file_name_time)


def parse_from_sptrans(df):
    # Defining the schema of the JSON
    schema = types.StructType(
        [
            types.StructField("hr", types.StringType(), True),
            types.StructField(
                "l",
                types.ArrayType(
                    types.StructType(
                        [
                            types.StructField("c", types.StringType(), True),
                            types.StructField("cl", types.IntegerType(), True),
                            types.StructField("sl", types.IntegerType(), True),
                            types.StructField("lt0", types.StringType(), True),
                            types.StructField("lt1", types.StringType(), True),
                            types.StructField("qv", types.IntegerType(), True),
                            types.StructField(
                                "vs",
                                types.ArrayType(
                                    types.StructType(
                                        [
                                            types.StructField(
                                                "p", types.StringType(), True
                                            ),
                                            types.StructField(
                                                "a", types.BooleanType(), True
                                            ),
                                            types.StructField(
                                                "ta", types.StringType(), True
                                            ),
                                            types.StructField(
                                                "py", types.DoubleType(), True
                                            ),
                                            types.StructField(
                                                "px", types.DoubleType(), True
                                            ),
                                            types.StructField(
                                                "sv", types.NullType(), True
                                            ),
                                            types.StructField(
                                                "is", types.NullType(), True
                                            ),
                                        ]
                                    )
                                ),
                                True,
                            ),
                        ]
                    )
                ),
                True,
            ),
            types.StructField(
                "company_data",
                types.ArrayType(
                    types.StructType(
                        [
                            types.StructField(
                                "code_area_operation", types.IntegerType(), True
                            ),
                            types.StructField(
                                "company_reference_code", types.IntegerType(), True
                            ),
                            types.StructField("company_name", types.StringType(), True),
                        ]
                    )
                ),
            ),
        ]
    )
    """
    Parsing the JSON
    """
    udf_function = udf(lambda z: decode_data(z))
    initial_df = df.select(
        col("key").cast(types.StringType()), udf_function(col("value")).alias("value")
    )
    initial_df = initial_df.select(
        from_json(col("value"), schema).alias("data")
    ).select("data.*")

    df_parsed = (
        initial_df.withColumn("line_info", explode("l"))
        .withColumn("company_info", explode("company_data"))
        .select("line_info.*", "company_info.*")
        .withColumn("vehicle_info", explode("vs"))
        .select("*", "vehicle_info.*")
        .drop("vs", "vehicle_info", "company_info")
    )

    # Defining a timestamp column
    df_parsed = df_parsed.withColumn(
        "timestamp", current_timestamp().cast(types.TimestampType())
    )

    """
    Counting the total of stopped buses by company
    """
    df_count = (
        df_parsed.withWatermark("timestamp", "2 minutes")
        .groupBy(
            window(col("timestamp"), "2 minutes"),
            "timestamp",
            "code_area_operation",
            "company_reference_code",
            "company_name",
            "qv",
        )
        .agg(count("*").alias("total_stopped_buses"))
        .drop("qv", "window")
    )
    return df_count


def rename_file_bucket(year, month, day, hour, file_name_time):
    bucket_name = "data_lake_bus_data_bus-data-389717"
    file_prefix = f"year={year}/month={month}/day={day}/hour={hour}/part"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blobs = storage_client.list_blobs(bucket_name, prefix=file_prefix)

    blob_file_name = [blob.name for blob in blobs][0]

    blob = bucket.blob(blob_file_name)

    bucket.rename_blob(
        blob, f"{file_prefix}_{str(uuid.uuid4())}" + "_" + f"{file_name_time}.csv"
    )


def parse_running_buses(df_kafka):
    schema = types.StructType(
        [
            types.StructField("c", types.StringType(), True),
            types.StructField("cl", types.IntegerType(), True),
            types.StructField("qv", types.IntegerType(), True),
        ]
    )
    udf_function = udf(lambda z: decode_data(z))
    initial_df = df_kafka.select(
        col("key").cast(types.StringType()), udf_function(col("value")).alias("value")
    )
    df_parsed = initial_df.select(from_json(col("value"), schema).alias("data")).select(
        "data.*"
    )
    return df_parsed


def foreach_batch_function_save_file_running_buses(df, epoch_id):
    """Function to aggregates companies with the same id by the code area operation"""
    date_time = datetime.now(ZoneInfo("America/Sao_Paulo"))
    date = date_time.strftime("%Y-%m-%d")
    time = date_time.strftime("%H")
    year = date.split("-")[0]
    month = date.split("-")[1]
    day = date.split("-")[2]
    # file_name_time = date_time.strftime("%H:%M:%S")

    # current_timestamp().cast(types.TimestampType()
    df.withColumn(
        "timestamp", from_utc_timestamp(current_timestamp(), "America/Sao_Paulo")
    ).repartition(1).write.mode("append").csv(
        f"gs://data_lake_bus_data_bus-data-389717/running_buses/year={year}/month={month}/day={day}/hour={time}"
    )


def sink_file_running_buses(df, processing_time: str = "2 minute"):
    """Sink method for kafka file output"""
    # date_time = datetime.now(ZoneInfo("America/Sao_Paulo"))
    # date = date_time.strftime("%Y-%m-%d")
    # time = date_time.strftime("%H")
    # year = date.split("-")[0]
    # month = date.split("-")[1]
    # day = date.split("-")[2]

    write_query = (
        df.writeStream.option("checkpointLocation", "asssadxx/checkpoint")
        .trigger(processingTime=processing_time)
        .outputMode("update")
        .foreachBatch(foreach_batch_function_save_file_running_buses)
        .start()
    )
    return write_query


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Kafka Consumer")
    parser.add_argument("--topic", help="topic name (readStream)")
    args = parser.parse_args()

    # Initiates spark
    conf = (
        SparkConf()
        .setAppName("test")
        .set("spark.hadoop.google.cloud.auth.service.account.enable", "true")
        .set(
            "spark.hadoop.google.cloud.auth.service.account.json.keyfile",
            "/opt/workspace/.google/bus-data-389717-3c31a20fe458.json",
        )
        .set("spark.sql.session.timeZone", "UTC")
    )

    sc = SparkContext(conf=conf)

    sc._jsc.hadoopConfiguration().set(
        "fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS"
    )
    sc._jsc.hadoopConfiguration().set(
        "fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"
    )
    sc._jsc.hadoopConfiguration().set(
        "fs.gs.auth.service.account.json.keyfile",
        "/opt/workspace/.google/bus-data-389717-3c31a20fe458.json",
    )
    sc._jsc.hadoopConfiguration().set("fs.gs.auth.service.account.enable", "true")

    spark = (
        SparkSession.builder.config(conf=sc.getConf()).appName("as123sc").getOrCreate()
    )

    # Reads data from kafka topic
    df_kafka = read_data_from_kafka(topic_name=args.topic)

    # Parsing
    # df_parsed = parse_from_sptrans(df_kafka)

    df_parsed = parse_running_buses(df_kafka)
    # sink_console(df_parsed, "append", "2 minutes")
    sink_file_running_buses(df_parsed)

    # Sinks
    # sink_console(df_parsed, "complete", "2 minutes")
    # sink_file(df_parsed)

    spark.streams.awaitAnyTermination()
