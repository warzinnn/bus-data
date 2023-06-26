import json
import time

from src.producer import BusProducer

"""
    File to run the Kafka producer
"""

if __name__ == "__main__":
    producer_config = {
        "bootstrap_servers": "localhost:9092",
        "key_serializer": lambda x: x.encode("utf-8"),
        "value_serializer": lambda x: json.dumps(x).encode("utf-8"),
        "acks": 1,
    }
    producer = BusProducer(producer_config)

    topic = "running-buses"

    # buses_companies = producer.map_buses_companies()

    while True:
        try:
            # records = producer.map_stopped_buses_garage_raw(buses_companies)
            records = producer.running_buses_by_line()
            producer.publish_data(topic=topic, records=records)
            time.sleep(55 * 2)
        except KeyboardInterrupt:
            print("Canceled by user.")
            break
        except Exception:
            continue
