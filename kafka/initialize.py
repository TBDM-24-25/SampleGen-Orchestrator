from confluent_kafka.admin import AdminClient, NewTopic
from time import sleep
import socket
import logging

# using print instead of logging, accepted in this use case, available in stdout
print('The initialization of Management Topics has started')

management_topics = [
    {'topic_name': 'Job_Handling', 'num_partitions': 1, 'replication_factor': 1},
    {'topic_name': 'Job_Status', 'num_partitions': 1, 'replication_factor': 1},
    {'topic_name': 'Agent_Status', 'num_partitions': 1, 'replication_factor': 1}
]

# checking for topic existence is not necessary, Kafka deals with this matter by itself
topics_to_create = [
    NewTopic(topic=management_topic.get('topic_name'),
    num_partitions=management_topic.get('num_partitions'),
    replication_factor=management_topic.get('replication_factor'))
    for management_topic in management_topics
]

max_retries = 10
retry_count = 0

while retry_count < max_retries:
    try:
        # AF_INET = address familiy internet, meaning ipv4
        # SOCK_STREAM = connection-oriented communication, meaning TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(('kafka', 9093))
            print('The Connection Check to Kafka has succeeded')
        # with block ensures that socket after block will be closed automatically

        kafka_admin_client = AdminClient({
            'bootstrap.servers': 'kafka:9093'
        })

        kafka_admin_client.create_topics(topics_to_create)
        print('The Management Topics have been created successfully')

        # break while True loop, jump to final success message
        break
    except Exception as e:
        retry_count += 1
        print(f'The Connection Check to Kafka has not succeeded yet: {e}')
        sleep(1)

# final success or failure message
if retry_count < max_retries:
    print('The initialization of Management Topics has been successful')
else:
    print('The initialization of Management Topics has not been successful, maximum number of retries reached')
    exit(1)
