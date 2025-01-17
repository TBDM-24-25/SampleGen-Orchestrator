from celery import shared_task
from .services.common_service import render_job_instruction_message
from .models import EnviromentVariable
from .services.kafka_service import KafkaService
from .services.logger_service import GlobalLogger
from .services.avro_service import AvroService
from .services.schema_registry_service import SchemaRegistryService
import os
from datetime import datetime
from time import sleep
from .models import Job

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


@shared_task
def stop_job(job):
    """stops the job by sending a stop message to the kafka topic"""
    kafka_service = KafkaService(group_id='job_status_consumers') # TODO: Check if this is the correct group_id
    topic_name = 'Job_Instruction'

    schema_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'schemes', 'job_handling.avsc')
    with open(schema_path, 'r') as f:
        job_handling_schema_str = f.read()

    schema_registry_client = SchemaRegistryService().get_client()
    job_handling_avro_serializer = AvroService(schema_registry_client, job_handling_schema_str).get_avro_serializer()

    # send stop message to kafka topic


@shared_task
def monitor_agent_status():
    """monitors the agents in the database and updates the status of the agents"""
    kafka_service = KafkaService(group_id='agent_status_consumers')
    topic_name = 'Agent_Status'

    schema_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'schemes', 'agent_status.avsc')
    with open(schema_path, 'r') as f:
        agent_status_schema_str = f.read()

    schema_registry_client = SchemaRegistryService().get_client()
    agent_status_avro_serializer = AvroService(schema_registry_client, agent_status_schema_str).get_avro_deserializer()

    # receive messages from kafka topic with avro serialization with confluent_kafka

@shared_task
def monitor_job_status():
    """monitors the jobs in the database and updates the status of the jobs"""
    kafka_service = KafkaService(group_id='job_status_consumers')
    topic_name = 'Job_Status'

    schema_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'schemes', 'job_status.avsc')
    with open(schema_path, 'r') as f:
        job_status_schema_str = f.read()

    schema_registry_client = SchemaRegistryService().get_client()
    job_status_avro_serializer = AvroService(schema_registry_client, job_status_schema_str).get_avro_deserializer()

    # receive messages from kafka topic with avro serialization with confluent_kafka


@shared_task
def permanent_background_task():
    iterator = 0
    while iterator < 10:
        print("This is a permanent background task that prints every 5 seconds")
        sleep(2)
        random_job = Job.objects.order_by('?').first()
        print(f"Random job: {random_job.name}")
        iterator += 1



    