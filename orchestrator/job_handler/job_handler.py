from orchestrator.services.kafka_service import KafkaService
from orchestrator.services.logger_service import GlobalLogger
from orchestrator.services.avro_service import AvroService
from orchestrator.services.schema_registry_service import SchemaRegistryService

# Mock data
job_instruction_data = {
    "operation": "create",
    "topic": "temperature",
    "container_image_name": "nginx",
    "number_of_containers": 1,
    "resource_limits": {
        "cpu": 1.0,
        # memory limits, string, with unit identifier such as b, k, m, g
        "memory": "1g"
    },
    "environment_variables": {
        "PYTHON_VERSION": "3.7",
        "SPARK_VERSION": "3.0.0"
    },
    "metadata": {
        "user": "user",
        "job_id": "job0001",
        "timestamp": 1734093178.392204,
        "description": "This job generates temperature data for IoT simulation.",
        "computation_duration_in_seconds": 3600,
        # can be None for creation jobs or even be omitted
        "container_id": ["33e6ef97f8f835d30f90767923c6fbe072142226f92c3bf9e5bbaf50d0939878"],
        "agent_id": "88:4d:7c:dc:93:0f"
    }
}

# initialize logger
logger = GlobalLogger(filename='orchestrator/job_handler/logfile.log', logger_name='job_handler_logger').get_logger()

with open("schemas/job_instruction.avsc", 'r') as f:
    job_instruction_schema_str = f.read()
    
schema_registry_client = SchemaRegistryService().get_client()
job_instruction_avro_serializer = AvroService(schema_registry_client, job_instruction_schema_str).get_avro_serializer()

def main():
    kafka_service = KafkaService(group_id='job_status_consumers', logger=logger)

    topic_name = 'Job_Instruction'

    try:
        kafka_service.send_message(topic_name, job_instruction_data, job_instruction_avro_serializer)
    except RuntimeError as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    main()
