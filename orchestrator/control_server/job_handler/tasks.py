from celery import shared_task
from .services.common_service import render_job_instruction_message
from .models import EnviromentVariable
from .services.kafka_service import KafkaService
from .services.logger_service import GlobalLogger
from .services.avro_service import AvroService
from .services.schema_registry_service import SchemaRegistryService
import os
from datetime import datetime

@shared_task
def start_job_task(job):
    """sets up the job data and submits the job to the kafka topic"""
    # Get job to be deployed
    enviroment_variables = EnviromentVariable.objects.filter(job=job)
    job_instruction_message = render_job_instruction_message(job, enviroment_variables)

    # Construct the path to the job_handling.avsc file
    current_dir = os.path.dirname(__file__)
    schema_path = os.path.join(current_dir, '..', '..', '..', 'schemes', 'job_handling.avsc')

    # Open and read the schema file
    with open(schema_path, 'r') as f:
        job_handling_schema_str = f.read()
        
    schema_registry_client = SchemaRegistryService().get_client()
    job_handling_avro_serializer = AvroService(schema_registry_client, job_handling_schema_str).get_avro_serializer()

    kafka_service = KafkaService(group_id='job_status_consumers')

    topic_name = 'Job_Instruction'
    try:
        kafka_service.send_message(topic_name, job_instruction_message, job_handling_avro_serializer)
        print(f"Job {job.id} submitted to Kafka topic")
        timestamp = job_instruction_message["metadata"]["timestamp"]
        # refactor from time to datetime format
        job.kafka_timestamp = datetime.fromtimestamp(timestamp)
        job.save()
    except RuntimeError as e:
        print(f"Error sending message: {e}")


