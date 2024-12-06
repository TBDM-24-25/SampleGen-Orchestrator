import json
from confluent_kafka import Producer, Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic

from orchestrator.services.config import KafkaConfig

class KafkaService:

    def __init__(self, group_id: str):
        kafka_config = KafkaConfig()
        self.kafka_base_config = {
            'bootstrap.servers': kafka_config.bootstrap_servers
        }

        self.kafka_consumer_config = {
            'group.id': group_id,
            # earliest resets the offset to the earliest (oldest) offset
            'auto.offset.reset': 'earliest',
            # disable auto commit to have self-control over offset commit
            'enable.auto.commit': False
            }

        self.kafka_producer = Producer(self.kafka_base_config)
        # merging kafka_base_config dictionary with kafka_consumer_config dictionary
        self.kafka_consumer = Consumer(self.kafka_consumer_config | self.kafka_base_config)
        self.kafka_admin_client = AdminClient(self.kafka_base_config)

    def create_topic(self, topic_name):
        # Check if the topic already exists
        existing_topics = self.kafka_admin_client.list_topics().topics
        if topic_name in existing_topics:
            raise ValueError(f"Topic {topic_name} already exists")

        # Create the new topic
        # TODO - @leandro, @frederico, @christian, discuss about replication factor and chose value accordingly
        new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
        fs = self.kafka_admin_client.create_topics([new_topic])

        for topic, f in fs.items():
            try:
                f.result()
                print(f"Topic {topic} created")
            except KafkaError as e:
                raise RuntimeError(f"Failed to create topic {topic}: {e}")

    def send_message(self, topic_name, message):
        # json.dumps(message).encode('utf-8') to serialise into JSON, encoded in utf-8
        self.kafka_producer.produce(topic_name, json.dumps(message).encode('utf-8'))
        self.kafka_producer.flush()
        print(f"Message '{message}' sent to topic '{topic_name}'")

    def consume_messages(self, topic: list, message_handler: callable) -> dict:
        self.kafka_consumer.subscribe(topic)

        try:
            while True:
                # Consumer.poll() consuming a single message, calls callbacks and returns events
                # 1 (in seconds) is the maximum time to block waiting for message, event or callback
                message = self.kafka_consumer.poll(1.0)
                if message is None:
                    print('no new message found')
                    continue
                # checking for the returned Message object's Message.error() necessary
                if message.error():
                    if message.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        print(f"Reached end of partition for topic {message.topic()} partition {message.partition()}")
                    elif message.error():
                        raise KafkaError(message.error())
                else:
                    # as message is a byte representation of string, decoding in utf-8 necessary
                    message_decoded = message.value().decode('utf-8')
                    # transforming string representation into dictionary, return value
                    message_dict = json.loads(message_decoded)
                    # callback, allowing for individual message processing
                    message_handler(message_dict)
                    # commit manually
                    self.kafka_consumer.commit(message=message)
        except KeyboardInterrupt:
            print("Consumer interrupted")
        except RuntimeError:
            print("Called on a closed consumer")
        finally:
            self.kafka_consumer.close()