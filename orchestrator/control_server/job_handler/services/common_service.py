from datetime import date, datetime
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from ..models import Agent
import os
import time



def json_serial_date_time(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

def render_job_instruction_message(job, enviroment_variables):
    # Prepare dictionary with enviroment variables. The KAFKA_TOPIC and KAFKA_BOOTSTRAP_SERVERS_DOCKER are required
    load_dotenv()
    prepared_enviroment_variables = {}
    try:
        KAFKA_BOOTSTRAP_SERVERS_DOCKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS_DOCKER")
        prepared_enviroment_variables["KAFKA_TOPIC"] = job.iot_data_kafka_topic
        prepared_enviroment_variables["KAFKA_BOOTSTRAP_SERVERS_DOCKER"] = KAFKA_BOOTSTRAP_SERVERS_DOCKER
    except AttributeError as e:
        print(f"AttributeError: {e}")
        prepared_enviroment_variables = {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        prepared_enviroment_variables = {}
    # Load the remaining enviroment variables from the DB and add them in the dictionary
    try:
        for enviroment_variable in enviroment_variables:
            prepared_enviroment_variables[enviroment_variable.variable_name] = enviroment_variable.variable_value
    except TypeError:
        print(f"TypeError: {e} - Check if 'enviroment_variables' is iterable.")
        prepared_enviroment_variables = {}
    except AttributeError as e:
        print(f"AttributeError: {e} - Check if 'enviroment_variable' has the correct attributes.")
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

    return job_instruction_data


def update_agent_status(message: dict) -> None:
    """Updates the agent status in the database according to the received Kafka message from the Agent_Status topic."""
    # TODO: To check if the operation field has the value heartbeat is currently not necessary, this must be checked later
    agent_status = message.get("status")
    agent_id = message.get("agent_id")
    kafka_timestamp = message.get("timestamp")
    containers_running = message.get("containers_running")

    # Get the agent instance from the database

