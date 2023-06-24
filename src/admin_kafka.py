from kafka.admin import KafkaAdminClient, NewTopic

if __name__ == "__main__":
    admin_client = KafkaAdminClient(
        bootstrap_servers="localhost:9092", client_id="bus-data"
    )
    topic_list = []
    topic_list.append(
        NewTopic(name="running-buses", num_partitions=1, replication_factor=1)
    )
    ct = admin_client.create_topics(new_topics=topic_list, validate_only=False)
    print(ct)
