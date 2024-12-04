from confluent_kafka import Producer, KafkaError, Consumer, Message
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.serialization import SerializationContext, MessageField

from config import KafkaConfig
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer

from models import Job
from services.schema_registry_service import SchemaRegistryService


class KafkaService:

    def __init__(self):
        self.__initialize_kafka_client()
        self.__create_topic()
        self.schema_registry_service = SchemaRegistryService()

    def __initialize_kafka_client(self):
        kafka_config = KafkaConfig()
        self.kafka_config = {
            'bootstrap.servers': kafka_config.bootstrap_servers
        }
        self.producer = Producer(self.kafka_config)
        self.admin_client = AdminClient(self.kafka_config)
        self.topic_name_job_request = kafka_config.topic_name_job_request

    def __create_topic(self):
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


    def __serialize_message(self, job: Job):
        latest_schema_version, schema_registry_client = self.schema_registry_service.get_schema_and_registry_client()
        avro_serializer = AvroSerializer(schema_str=latest_schema_version.schema_str,
                                         schema_registry_client=schema_registry_client,
                                         conf={
                                              'auto.register.schemas': False
                                            }
                                         )
        serialization_context = SerializationContext(self.topic_name_job_request, MessageField.VALUE)
        serialized_message = avro_serializer(job.model_dump(), serialization_context)
        return serialized_message

    def __deserialize_message(self, message: Message) -> Job:
        latest_schema_version, schema_registry_client = self.schema_registry_service.get_schema_and_registry_client()
        avro_deserializer = AvroDeserializer(
            schema_registry_client=schema_registry_client,
            schema_str=latest_schema_version.schema_str,
        )
        job_dictionary = avro_deserializer(message.value(), SerializationContext(message.topic(), MessageField.VALUE))
        job = Job.model_validate(job_dictionary)
        return job

    def send_job(self, job: Job):
        serialized_message = self.__serialize_message(job)
        self.producer.produce(self.topic_name_job_request, serialized_message)


    def consume_messages(self, group_id, process_message):
        consumer_config = {
            'bootstrap.servers': self.kafka_config['bootstrap.servers'],
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        consumer = Consumer(consumer_config)
        consumer.subscribe([self.topic_name_job_request])

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
                    job = self.__deserialize_message(msg)
                    process_message(job)
        except KeyboardInterrupt:
            print("Consumer interrupted")
        finally:
            consumer.close()
