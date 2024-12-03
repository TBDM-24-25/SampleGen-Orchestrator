from confluent_kafka import Producer, KafkaError, Consumer, Message
from confluent_kafka.admin import AdminClient, NewTopic
from config import KafkaConfig, SchemaRegistryConfig
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.schema_registry.avro import AvroSerializer


class KafkaService:

    def __init__(self):
        self.__initialize_kafka()
        self.__initialize_schema_registry()

    def __initialize_kafka(self):
        kafka_config = KafkaConfig()
        self.kafka_config = {
            'bootstrap.servers': kafka_config.bootstrap_servers
        }
        self.producer = Producer(self.kafka_config)
        self.admin_client = AdminClient(self.kafka_config)
        self.topic_name_job_request = kafka_config.topic_name_job_request
        self.__initialize_topic()

    def __initialize_schema_registry(self):
        schema_registry_config = SchemaRegistryConfig()
        self.schema_registry_config = {
            'url': schema_registry_config.schema_registry_url
        }
        self.schema_registry_client = SchemaRegistryClient(self.schema_registry_config)

    def __initialize_topic(self):
        # Check if the topic already exists
        existing_topics = self.admin_client.list_topics().topics
        if self.topic_name_job_request in existing_topics:
            print(f"Topic {self.topic_name_job_request} already exists")
            return

        # Create the new topic
        new_topic = NewTopic(self.topic_name_job_request, num_partitions=1, replication_factor=1)
        fs = self.admin_client.create_topics([new_topic])

        for topic, f in fs.items():
            try:
                f.result()
                print(f"Topic {topic} created")
            except KafkaError as e:
                raise RuntimeError(f"Failed to create topic {topic}: {e}")


    def __create_job_message(self, job):
        with open(f"../../schema_registry/job_config.avsc") as f:
            schema_str = f.read()

        schema = Schema(schema_str, 'AVRO')
        self.schema_registry_client.register_schema(f"job_config", schema)
        avro_serializer = AvroSerializer(schema_registry_client=self.schema_registry_client, schema_str=schema_str)
        serialized_message = avro_serializer(job, None)
        return serialized_message

    def send_job(self, job):
        serialized_message = self.__create_job_message(job)
        self.producer.produce(self.topic_name_job_request, serialized_message)


    def consume_messages(self, topic, group_id, process_message):
        consumer_config = {
            'bootstrap.servers': self.kafka_config['bootstrap.servers'],
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        consumer = Consumer(consumer_config)
        consumer.subscribe(topic)

        try:
            while True:
                msg = consumer.poll(1.0)  # Poll for messages with a timeout of 1 second
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        print(f"Reached end of partition for topic {msg.topic()} partition {msg.partition()}")
                    elif msg.error():
                        raise KafkaError(msg.error())
                else:
                    # Process the message
                    process_message(msg)
        except KeyboardInterrupt:
            print("Consumer interrupted")
        finally:
            consumer.close()
