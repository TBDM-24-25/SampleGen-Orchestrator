from time import sleep
from celery import shared_task
from .services import render_job_instruction_message
from .models import EnviromentVariable
from orchestrator.services.kafka_service import KafkaService
from orchestrator.services.logger_service import GlobalLogger
from orchestrator.services.avro_service import AvroService
from orchestrator.services.schema_registry_service import SchemaRegistryService

@shared_task
def start_job_task(job):
    """sets up the job data and submits the job to the kafka topic"""
    # sleep(10)
    print(f"job with id {job.id} has started")

    # Render the job instruction message
    enviroment_variables = EnviromentVariable.objects.filter(job=job)
    rendered_message = render_job_instruction_message(
        operation="create",
        container_image_name=job.container_image_name,
        number_of_containers=job.container_number,
        container_cpu_limit=job.container_cpu_limit,
        container_memory_limit=job.container_memory_limit_in_mb,
        enviroment_variables=enviroment_variables,
        user="test_user",
        job_id=job.id,
        timestamp=job.updated_at,
        job_description="This is a test job",
        computation_duration_in_seconds=job.computation_duration_in_seconds,
    )
    print(rendered_message)

    # Submit the job to the Kafka topic with avro schema validation
    # This is a placeholder for the actual Kafka submission


