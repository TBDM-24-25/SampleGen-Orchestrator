from datetime import date, datetime
from dotenv import load_dotenv
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models import Agent, Job, JobStatus, Container, ContainerStatus
import os
import time
import logging



def json_serial_date_time(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

def render_start_job_instruction_message(job, enviroment_variables):
    logger = get_global_logger()
    # Prepare dictionary with enviroment variables. The KAFKA_TOPIC and KAFKA_BOOTSTRAP_SERVERS_DOCKER are required
    load_dotenv()
    prepared_enviroment_variables = {}
    try:
        KAFKA_BOOTSTRAP_SERVERS_DOCKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS_DOCKER")
        prepared_enviroment_variables["KAFKA_TOPIC"] = job.iot_data_kafka_topic
        prepared_enviroment_variables["KAFKA_BOOTSTRAP_SERVERS_DOCKER"] = KAFKA_BOOTSTRAP_SERVERS_DOCKER
    except AttributeError as e:
        logger.error(f"AttributeError: {e}")
        prepared_enviroment_variables = {}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        prepared_enviroment_variables = {}
    # Load the remaining enviroment variables from the DB and add them in the dictionary
    try:
        for enviroment_variable in enviroment_variables:
            prepared_enviroment_variables[enviroment_variable.variable_name] = enviroment_variable.variable_value
    except TypeError:
        logger.error(f"TypeError: {e} - Check if 'enviroment_variables' is iterable.")
        prepared_enviroment_variables = {}
    except AttributeError as e:
        logger.error(f"AttributeError: {e} - Check if 'enviroment_variable' has the correct attributes.")
        prepared_enviroment_variables = {}

    # Prepare the container memory limit string. DB stores the value in MB as an integer.
    # Example 2000m for 2000 MB or 2 GB
    container_memory_limit_in_mb = f"{str(job.container_memory_limit_in_mb)}m"
    timestamp = time.time()

    # Prepare the job instuction data as a dictionary
    job_instruction_data = {
        "operation": "create",
        "container_image_name": job.container_image_name,
        "number_of_containers": job.container_number,
        "resource_limits": {
            "cpu": job.container_cpu_limit,
            "memory": container_memory_limit_in_mb
        },
        "environment_variables": prepared_enviroment_variables,
        "metadata": {
            "user": "user",
            "job_id": str(job.id),
            "timestamp": timestamp, 
            "description": job.description,
            "computation_duration_in_seconds": job.computation_duration_in_seconds
        }
    }

    logger.info(f"Start job instruction message for job with ID {job.id} prepared.")
    return job_instruction_data


def render_stop_job_instruction_message(job):
    """Prepares the stop job instruction message as a dictionary.
    The message contains the following parameters: operation, number_of_containers, job_id, container_image_name, container_id (all the containers related to the job, represented as a json array)
    The parameters: user, timestamp, description, computation_duration_in_seconds are also included in the metadata field for logging purposes in the container_handler and consistency."""
    
    logger = get_global_logger()
    # The timestamp is also provided in the stop job instruction message
    timestamp = time.time()

    # Prepare the job instuction data as a dictionary
    try:
        job_stop_instruction_data = {
            "operation": "delete",
            "container_image_name": job.container_image_name,
            "number_of_containers": job.container_number,
            "resource_limits": {
                "cpu": job.container_cpu_limit,
                "memory": f"{job.container_memory_limit_in_mb}m"
            },
            "environment_variables": {},
            "metadata": {
                "user": "user",
                "job_id": str(job.id),
                "timestamp": timestamp, 
                "description": job.description,
                "computation_duration_in_seconds": job.computation_duration_in_seconds,
                "container_id": [container.docker_container_id for container in job.container_set.all()],
                "agent_id": job.agent.docker_agent_id
            }
        }
    except AttributeError as e:
        logger.error(f"AttributeError: {e} - Check if the job and the related containers have the correct attributes.")
        job_stop_instruction_data = {} 
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        job_stop_instruction_data = {}

    logger.info(f"Stop job instruction message for job with ID {job.id} prepared.")
    return job_stop_instruction_data


def update_agent_status(message: dict) -> None:
    """
    Updates the agent status in the database according to the received Kafka message from the Agent_Status topic.
    If the agent does not exist in the database, a new agent will be created.
    """
    logger = get_global_logger()

    try:
        agent_status = message.get("status")
        meta_data = message.get("metadata")
        agent_id = meta_data.get("agent_id")
        kafka_timestamp = meta_data.get("timestamp")
        containers_running = meta_data.get("containers_running")
    except AttributeError as e:
        logger.error(f"AttributeError: {e} - Check if the message has the correct attributes.")
        return
    
    # Convert the timestamp to a string in ISO 8601 format
    try:
        kafka_timestamp = datetime.fromtimestamp(kafka_timestamp, tz=timezone.utc)
    except (TypeError, ValueError) as e:
        logger.error(f"Error converting timestamp: {e}")
        return
    
    agent = None
    try:
        # Update or create the agent
        agent, created = Agent.objects.update_or_create(
            docker_agent_id=agent_id,
            defaults={
                'status': agent_status,
                'kafka_timestamp': kafka_timestamp,
                'updated_at': datetime.now()
            }
        )
        if created:
            logger.info(f"Agent with ID {agent.docker_agent_id} created and stored in database.")
        else:
            logger.info(f"Agent with ID {agent.docker_agent_id} updated.")

        send_update_to_job_consumer_group()
    except Exception as e:
        logger.error(f"Error updating or creating agent: {e}")
        return
    finally:
        logger.info(f"Agent status handling for agent with ID {agent_id} completed.")
    
    # Leads back to the process of waiting for the next message
    return

def update_job_status(message: dict) -> None:
    """
    Updates the job status in the database according to the received Kafka message from the Job_Status topic.
    If the job does not exist in the database, the message will be ignored. This message must handle both cases
    start and stop job since there is no control in the KafkaConsumer commit offset.
    """
    logger = get_global_logger()

    try:
        operation = message.get("operation")
        status = message.get("status")
        docker_container_ids = message.get("container_id")
        meta_data = message.get("metadata")
        job_id = meta_data.get("job_id")
        agent_id = meta_data.get("agent_id")
        kafka_timestamp = meta_data.get("timestamp")
        logger.info(f"Job status handling for job with ID {job_id} started.")
    except AttributeError as e:
        logger.error(f"AttributeError: {e} - Check if the message has the correct attributes.")
        return
    
    if status != "successful":
        logger.warning(f"Job with ID {job_id} failed on operation: {operation}.")
        return
    
    # Convert the timestamp to a timezone-aware datetime object
    try:
        kafka_timestamp = datetime.fromtimestamp(kafka_timestamp, tz=timezone.utc)
    except (TypeError, ValueError) as e:
        logger.error(f"Error converting timestamp: {e}")
        return
    
    # Update the job status in the database
    try:
        # Set the common attributes of the job
        job = Job.objects.get(pk=job_id)
        job.latest_operation = operation
        job.kafka_timestamp = kafka_timestamp
        logger.info(f"Common attributes of existing Job with ID {job_id} stored in memory.")
    except Job.DoesNotExist:
        logger.warning(f"Job with ID {job_id} not found.")
        return
    except Exception as e:
        logger.error(f"Error updating job: {e}")
        return

    # Update the job and the corresponding entities according to the operation
    if operation == "create":
        update_started_job(job, agent_id, docker_container_ids)
    elif operation == "delete":
        update_stopped_job(job)
    else:
        logger.warning(f"Unknown operation: {operation}")
        return
    
    logger.info(f"Job status handling for job with ID {job.id} completed.")

    return


def update_started_job(job, agent_id, docker_container_ids):
    """Updates the job status to RUNNING and creates the related containers in the database."""
    logger = get_global_logger()

    # Update the job
    try:
        job.agent = Agent.objects.get(docker_agent_id=agent_id)
        job.updated_at = datetime.now(tz=timezone.utc)
        job.status = JobStatus.RUNNING
        job.save()
        logger.info(f"Job with ID {job.id} updated with agent ID {agent_id}.")
    except Agent.DoesNotExist:
        logger.error(f"Agent with ID {agent_id} not found.")
        return
    except Exception as e:
        logger.error(f"Error updating job: {e}")
        return
    
    # Create the related containers
    try:
        for container_id in docker_container_ids:
            container = Container.objects.create(
                status=ContainerStatus.RUNNING,
                docker_container_id=container_id,
                job=job,
                agent=job.agent
            )
            container.save()
            send_update_to_job_consumer_group()
            logger.info(f"Container with ID {container.id} created and stored in database.")

        logger.info(f"Containers for job with ID {job.id} created.")
    except Exception as e:
        logger.error(f"Error creating container: {e}")
    
    return


def update_stopped_job(job):
    """Updates the job status to COMPLETED and deletes the related containers from the database."""
    logger = get_global_logger()

    try:
        job.agent = None
        job.status = JobStatus.COMPLETED
        job.container_set.all().delete()
        job.updated_at = datetime.now(tz=timezone.utc)
        job.save()
        logger.info(f"Job with ID {job.id} updated.")

        send_update_to_job_consumer_group()
    except Exception as e:
        logger.error(f"Error updating stopped job: {e}")
        return
    
    logger.info(f"Job with ID {job.id} stopped.")

    return

def send_update_to_job_consumer_group():
    """Sends a message to the Job_Status topic to trigger the update of the job status in the database."""
    logger = get_global_logger()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "jobs", # Group name
        {
            "type": "fetch.jobs", # Method to invoke
        }
    )

    logger.info("Update sent to job consumer group.")
    return

def get_django_logger():
    return logging.getLogger("django")

def get_global_logger():
    return logging.getLogger("global_logger")