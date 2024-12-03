from confluent_kafka import Producer, KafkaError, Consumer, Message
from confluent_kafka.admin import AdminClient, NewTopic
from config import KafkaConfig


class KafkaService:

    def __init__(self):
        kafka_config = KafkaConfig()
        self.kafka_config = {
            'bootstrap.servers': kafka_config.bootstrap_servers
        }
        self.producer = Producer(self.kafka_config)
        self.admin_client = AdminClient(self.kafka_config)

    def create_topic(self, topic_name):
        # Check if the topic already exists
        existing_topics = self.admin_client.list_topics().topics
        if topic_name in existing_topics:
            raise ValueError(f"Topic {topic_name} already exists")

        # Create the new topic
        new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
        fs = self.admin_client.create_topics([new_topic])

        for topic, f in fs.items():
            try:
                f.result()
                print(f"Topic {topic} created")
            except KafkaError as e:
                raise RuntimeError(f"Failed to create topic {topic}: {e}")

    def send_message(self, topic_name, message):
        self.producer.produce(topic_name, message.encode('utf-8'))
        self.producer.flush()
        print(f"Message '{message}' sent to topic '{topic_name}'")

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
