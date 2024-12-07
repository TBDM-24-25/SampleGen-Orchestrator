from confluent_kafka.admin import AdminClient, NewTopic

from time import sleep
print('Start to wait 15 seconds', flush=True)
sleep(15)
print('Waited for 15 seconds', flush=True)
kafka_admin_client = AdminClient({
    'bootstrap.servers': 'kafka:9093'
})


# TODO - discuss about partitions,
initial_topics = [
    {'topic_name': 'Job_Handling', 'num_partitions': 1, 'replication_factor': 1},
    {'topic_name': 'Job_Status', 'num_partitions': 1, 'replication_factor': 1},
    {'topic_name': 'Agent_Status', 'num_partitions': 1, 'replication_factor': 1}
]

# checking if topics exist not necessary
topics_to_create = [
    NewTopic(topic=initial_topic.get('topic_name'),
    num_partitions=initial_topic.get('num_partitions'),
    replication_factor=initial_topic.get('replication_factor'))
    for initial_topic in initial_topics
]

kafka_admin_client.create_topics(topics_to_create)

print('Initial Topics Created')

sleep(5)
print(kafka_admin_client.list_topics().topics)





