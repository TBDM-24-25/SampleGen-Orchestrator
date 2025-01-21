from celery import shared_task
from .services.common_service import render_start_job_instruction_message, render_stop_job_instruction_message, update_agent_status, update_job_status
from .models import EnviromentVariable
from .services.kafka_service import KafkaService
from .services.logger_service import GlobalLogger
from .services.avro_service import AvroService
from .services.schema_registry_service import SchemaRegistryService
import os
from datetime import datetime
from django.utils import timezone
from time import sleep
from .models import Job, JobStatus
from datetime import timedelta

@shared_task
def start_job_task(job_id):
    """sets up the job data and submits the job to the kafka topic"""
    job = Job.objects.get(pk=job_id)
    # Get job to be deployed
    enviroment_variables = EnviromentVariable.objects.filter(job=job)
    job_instruction_message = render_start_job_instruction_message(job, enviroment_variables)

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
        print(f"Job {job.id} sent to Kafka topic")
        timestamp = job_instruction_message["metadata"]["timestamp"]
        # refactor from time to datetime format
        job.kafka_timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        job.status = JobStatus.DEPLOYING
        job.save()
    except RuntimeError as e:
        print(f"Error sending message: {e}")


@shared_task
def stop_job_task(job_id):
    """stops the job by sending a stop message to the kafka topic"""
    job = Job.objects.get(pk=job_id)
    print(f"Starting process of stopping job with ID {job.id}")
    # Job must be running to be stopped
    if job.status != JobStatus.RUNNING:
        print(f"Job {job.id} is not running, cannot stop")
        return
    
    stop_job_instruction_message = render_stop_job_instruction_message(job)
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
        print(f"Start sending stop message to Kafka topic")
        kafka_service.send_message(topic_name, stop_job_instruction_message, job_handling_avro_serializer)
        print(f"Job {job.id} stop message sent to Kafka topic")
        timestamp = stop_job_instruction_message["metadata"]["timestamp"]
        # refactor from time to datetime format
        job.kafka_timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        job.save()
        print(f"Job with ID {job.id} successfully submitted to Kafka topic")
    except RuntimeError as e:
        print(f"Error sending stop message: {e}")
    
    return


@shared_task
def monitor_agent_status():
    """monitors the agents in the database and updates the status of the agents"""
    try:
        kafka_service = KafkaService(group_id='agent_status_consumers')
        topic_name = 'Agent_Status'

        schema_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'schemes', 'agent_status.avsc')
        with open(schema_path, 'r') as f:
            agent_status_schema_str = f.read()

        schema_registry_client = SchemaRegistryService().get_client()
        agent_status_avro_serializer = AvroService(schema_registry_client, agent_status_schema_str).get_avro_deserializer()
        # receive messages from kafka topic with avro serialization with confluent_kafka
        kafka_service.consume_messages(
            topic_names=[topic_name],
            message_handler=update_agent_status,
            avro_deserializer=agent_status_avro_serializer
        )
    except Exception as e:
        print(f"Error monitoring agent status: {e}")


@shared_task
def monitor_job_status():
    """monitors the jobs in the database and updates the status of the jobs"""
    try:
        kafka_service = KafkaService(group_id='job_status_consumers')
        topic_name = 'Job_Status'

        schema_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'schemes', 'job_status.avsc')
        with open(schema_path, 'r') as f:
            job_status_schema_str = f.read()

        schema_registry_client = SchemaRegistryService().get_client()
        job_status_avro_serializer = AvroService(schema_registry_client, job_status_schema_str).get_avro_deserializer()

        # receive messages from kafka topic with avro serialization with confluent_kafka
        kafka_service.consume_messages(
            topic_names=[topic_name],
            message_handler=update_job_status,
            avro_deserializer=job_status_avro_serializer
        )
    except Exception as e:
        print(f"Error monitoring job status: {e}")


    
# @shared_task
# def job_stop_scheduler_task():
#     print("Starting job stop scheduler task")
#     """orchestrates the finished jobs by sending a stop message to the kafka topic"""
#     while True:
#         sleep(5)
#         jobs = Job.objects.filter(status=JobStatus.RUNNING)
    
#         if not jobs:
#             continue

#         for job in jobs:
#             try:
#                 # get time parameters
#                 current_time = timezone.now()
#                 job_start_time = job.kafka_timestamp
#                 computation_duration = job.computation_duration_in_seconds
#                 job_end_time = job_start_time + timedelta(seconds=computation_duration)
                
#                 # Ensure both datetime objects are timezone-aware
#                 if timezone.is_naive(job_end_time):
#                     job_end_time = timezone.make_aware(job_end_time)
                
#                 # check if the job has run for the specified duration
#                 if current_time >= job_end_time:
#                     print(f"Job {job.id} has run for the specified duration")
#                     print(f"Stopping job {job.id}")
#                     # Stop the job
#                     stop_job_task.delay(job.id)
#             except Exception as e:
#                 print(f"Error stopping job {job.id}: {e}")
#                 continue





# TODO: This function must be completed
@shared_task
def iot_data_subscription_sheduling_task():
    """schedules the iot data subscription task to run every 5 seconds"""
    while True:
        print("Subscribing to IoT data")
        sleep(5)
        # iot_data_subscription_task()


# TODO: This function must be completed
@shared_task
def iot_data_subscription_task():
    """subscribes to the iot data and sends the data to the kafka topic"""
    try:
        # Get iot data
        iot_data = []
        # create input directory and file for the iot data
        # subscribe to the iot data topic and pass function to consume_messages to handle the data
        # TODO: modify the consume_message function with an exit condition
        # You must adapt all other functions accordingly that already use the consume_messages function
        pass
    except Exception as e:
        print(f"Error subscribing to iot data: {e}")