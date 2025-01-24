import json
from confluent_kafka import Producer, Consumer, KafkaError
from confluent_kafka.admin import AdminClient

from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer

from .config import KafkaConfig
from .common_service import get_global_logger

logger = get_global_logger()

class KafkaService:

    def __init__(self, group_id: str):
        kafka_config = KafkaConfig()
        self.kafka_base_config = {
            'bootstrap.servers': kafka_config.bootstrap_servers_host
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

    def send_message(self, topic_name: str, message: dict, avro_serializer: AvroSerializer = None):
        try:        
            if avro_serializer is None:
                self.kafka_producer.produce(topic=topic_name,
                                            value= json.dumps(message).encode('utf-8'))
            else:
                self.kafka_producer.produce(topic=topic_name,
                                            value=avro_serializer(message, SerializationContext(topic_name, MessageField.VALUE)))
            self.kafka_producer.flush()
            logger.info('Message %s produced to Topic %s', message, topic_name)
        except Exception as e:
            logger.warning('Unable to produce Message %s to Topic %s due to %s', message, topic_name, e)

    def consume_messages(self, topic_names: list, message_handler: callable, avro_deserializer: AvroDeserializer = None) -> dict:

        self.kafka_consumer.subscribe(topic_names)

        try:
            while True:
                # Consumer.poll() consuming a single message, calls callbacks and returns events
                # 1 (in seconds) is the maximum time to block waiting for message, event or callback
                message = self.kafka_consumer.poll(1.0)
                if message is None:
                    continue
                # checking for the returned Message object's Message.error() necessary
                if message.error():
                    if message.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        logger.warning('''Reached End of Partition for Topic %s} 
                                         Partition %s''', message.topic, message.partition)
                    elif message.error():
                        raise KafkaError(message.error())
                else:
                    if avro_deserializer is None:
                        # as message is a byte representation of string, decoding in utf-8 necessary
                        message_decoded = message.value().decode('utf-8')
                        # transforming string representation into dictionary, return value
                        message_dict = json.loads(message_decoded)
                        # callback, allowing for individual message processing
                    else:
                        # avro deserializer returns a dict object, representing the message
                        message_dict = avro_deserializer(message.value(), SerializationContext(message.topic(), MessageField.VALUE))

                    logger.info('Message %s consumed from Topic %s', message_dict, topic_names)
                    # callback, allowing for individual message processing
                    message_handler(message_dict)
                    self.kafka_consumer.commit(message=message)
        except Exception as e:
            logger.warning('Unable to consume Message %s from Topic %s due to %s', message, topic_names, e)
        except KeyboardInterrupt:
            logger.warning('Consumer interrupted')
        finally:
            self.kafka_consumer.close()
