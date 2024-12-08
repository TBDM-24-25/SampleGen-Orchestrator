from orchestrator.services.kafka_service import KafkaService


service = KafkaService()

print(service.kafka_admin_client.list_topics().topics)