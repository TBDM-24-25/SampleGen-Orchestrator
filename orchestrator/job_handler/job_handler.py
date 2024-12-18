from orchestrator.services.kafka_service import KafkaService
from orchestrator.services.logger_service import GlobalLogger
from orchestrator.services.avro_service import AvroService
from orchestrator.services.schema_registry_service import SchemaRegistryService

# Mock data
job_instruction_data = {
    "operation": "delete",
    "container_image_name": "nginx",
    "number_of_containers": 2,
    "resource_limits": {
        "cpu": 1.0,
        # memory limits, string, with unit identifier such as b, k, m, g
        "memory": "1g"
    },
    "environment_variables": {
        "TOPIC": "temperature",
        "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092"
    },
    "metadata": {
        "user": "user",
        "job_id": "job0001",
        "timestamp": 1734093178.392204,
        "description": "This job generates temperature data for IoT simulation.",
        "computation_duration_in_seconds": 3600,
        # can be None for creation jobs or even be omitted
        "container_id": ["9e99c07cdd2597163f4f1d54ad2216169f39d57dd82b7ccccd750ee3e4e5dce4", "a6ba7a28f9f7ff1bc40611b5bfcb5edd258279942ef03b5f6417d334805977c1"],
        "agent_id": "88:4d:7c:dc:93:0f"
    }
}

# initialize logger
logger = GlobalLogger.get_logger()

with open("schemes/job_handling.avsc", 'r') as f:
    job_handling_schema_str = f.read()
    
schema_registry_client = SchemaRegistryService().get_client()
job_handling_avro_serializer = AvroService(schema_registry_client, job_handling_schema_str).get_avro_serializer()

def main():
    kafka_service = KafkaService(group_id='job_status_consumers')

    topic_name = 'Job_Instruction'

    try:
        kafka_service.send_message(topic_name, job_instruction_data, job_handling_avro_serializer)
    except RuntimeError as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    main()
