import threading
from time import sleep, time
import json
from getmac import get_mac_address
from jinja2 import Environment, FileSystemLoader

import docker
from docker.errors import DockerException

from orchestrator.services.kafka_service import KafkaService
from orchestrator.services.logger_service import GlobalLogger

from orchestrator.services.status import Status

# TODO - remove all print statements in the end
# TODO - @leandro during container creation, check resources?
# TODO - @leandro handle empty or invalid input?
# TODO - Finalize heartbeat agent, docker daemon check and resource check
# TODO - @leandro report number of containers/container ids really necessary?

# initialize logger
logger = GlobalLogger(filename='orchestrator/container_handler/logfile.log').get_logger()

# initialize KafkaService with group_id Job_Consumers
kafka_service = KafkaService(group_id='Job_Consumers')

# agent_id based on the MAC address of host machine
agent_id = get_mac_address()

# provide jinja2 environment
environment = Environment(loader=FileSystemLoader("templates/"))
# make function time accessible to jinja2 environment. Within template, get_timestamp() can be used
# reference to function time is handed over
environment.globals["get_timestamp"] = time
# make agent_id accessible to jinja2 environment, as used in every template
environment.globals["agent_id"] = agent_id

# initialize docker client with None
docker_client = None

# heartbeat check interval
check_interval = 10

def initialize_docker_client():
    '''
    The function attempts to initialize a docker client using the environment configuration.
    If successful, assigns the client to the global variable docker_client. 
    If the initialization fails, the DockerException is propagated to allow the caller
    to handle it.
        Parameters:
            None
        Returns:
            None
        Raises
            DockerException: If initialization of the Docker client fails
    
    '''
    global docker_client
    try:
        docker_client = docker.client.from_env()
    except DockerException:
        docker_client = None
        # reraise DockerException that agent observer can handle exception
        raise

def extract_message_values(message_dict: dict):
    '''
    The function extracts specific values from a
    message dictionary representing a job instruction.
        Parameters: 
            message_dict (dict): A dictionary containing the job instruction details
        Returns:
            tuple: A tuple containing:
                    - operation (str): The operation to perform (create or delete)
                    - number_of_containers (int): The number of containers involved in the job
                    - job_id (str): The job id
                    - container_image_name (str): The container image name
    '''
    operation = message_dict.get('operation')
    number_of_containers = message_dict.get('number_of_containers')
    job_id = message_dict.get('metadata').get('job_id')
    container_image_name = message_dict.get('container_image_name')

    return operation, number_of_containers, job_id, container_image_name

def extract_runtime_information(message_dict: dict):
    '''
    The function extracts runtime configuration details 
    from a given message dictionary representing a job instruction.
        Parameters: 
            message_dict (dict): A dictionary containing the job instruction details
        Returns:
            tuple: A tuple containing:
                    - cpu_limit_nano (int): The CPU limit in nanoseconds of CPU time per second
                    - memory_limit (str): The memory limit as a string
                    - environment_variables (dict): A dictionary of environment variable
    '''
    cpu_limit_raw = message_dict.get('resource_limits').get('cpu')
    # The nano_cpus parameter (see below) takes nanoseconds of CPU time per second as an input
    # 0.5 CPUs = 500_000_000
    # 1 CPU = 1_000_000_000
    # 2 CPUs = 2_000_000_000
    # therefore, the following calculation is necessary
    cpu_limit_nano = int(cpu_limit_raw * 1e9)

    memory_limit = message_dict.get('resource_limits').get('memory')
    environment_variables = message_dict.get('environment_variables')

    return cpu_limit_nano, memory_limit, environment_variables

def extract_container_ids(message_dict: dict) -> list:
    '''
    The function extracts container ids from a given 
    message dictionary representing a job instruction.
        Parameters: 
            message_dict (dict): A dictionary containing the job instruction details
        Returns:
            list: A list containing container ids
    '''
    return message_dict.get('metadata').get('container_id')

def render_job_template_and_produce_job_status_message(
        operation: str,
        status: Status,
        container_image_name: str,
        containers_created: list,
        job_id: str
) -> None:
    '''
    The function renders a job status template and 
    sends a job status message to Kafka.
        Parameters:
            operation (str): The type of operation performed (e.g., create, delete)
            status (Status): The status of the operation (e.g., Status.SUCCESS, Status.FAILURE)
            container_image_name (str): The name of the container image used
            containers_created (list): A list of container ids that were created as part of the job
            job_id (str): A unique identifier for the job
    Returns:
        None
    '''
    # load job_template
    job_template = environment.get_template('container_handler/job_status.json.j2')

    rendered_content = job_template.render(
    operation=operation,
    status=status.value,
    container_image_name=container_image_name,
    container_id=containers_created,
    job_id=job_id)

    content = json.loads(rendered_content)

    kafka_service.send_message('Job_Status', content)

def render_heartbeat_template_and_produce_agent_status_message(status: Status, failed_checks: list) -> None:
    '''
    The function renders a heartbead template and 
    sends a agent status message to Kafka.
        Parameters:
            status (Status): The status of the heartbeat (e.g., Status.SUCCESS, Status.FAILURE)
            failed_checks (list): A list (potentially empty) of checks that failed during the heartbeat
    Returns:
        None
    '''
    # load heartbeat_template
    heartbeat_template = environment.get_template("container_handler/heartbeat.json.j2")

    rendered_content = heartbeat_template.render(
        status=status.value,
        failed_checks=failed_checks
    )
    content = json.loads(rendered_content)

    kafka_service.send_message('Agent_Status', content)

def create_containers(
        number_of_containers: int,
        container_image_name: str,
        job_id: str,
        message_dict: dict
) -> None:
    '''
    The function creates the specified number of container(s) based on 
    the given image and provided job details.
        Parameters:
            number_of_containers (int): Number of containers to create
            container_image_name (str): Name of the container image to use
            job_id (str): Unique job identifier
            message_dict (dict): A Dictionary containing job instruction
        Returns:
            None
    '''
    # initialization of list, necessary to store container ID(s)
    containers_created = []

    # extract runtime information values
    cpu_limit_nano, memory_limit, environment_variables = extract_runtime_information(message_dict)

    for index in range(number_of_containers):
        logger.info('Starting Container %s/%s with Image %s',
                     index + 1, number_of_containers, container_image_name)
        try:
            container = docker_client.containers.run(
                image=container_image_name,
                mem_limit=memory_limit,
                nano_cpus=cpu_limit_nano,
                environment=environment_variables,
                labels=['sample_gen_orchestrator'],
                detach=True)

            container_id = container.id

            logger.info('Container %s/%s with Image %s has been successfully created, Container ID: %s',
                        index + 1, number_of_containers, container_image_name, container_id)

            containers_created.append(container_id)
            status = Status.SUCCESS

        except Exception as e:
            logger.info('Handling of Job Instruction for Job ID %s was not successful due to %s', job_id, e)
            status = Status.FAILURE
            # terminate for loop early
            break

    render_job_template_and_produce_job_status_message('create', status, container_image_name, containers_created, job_id)
    logger.info('Handling of Job Instruction for Job ID %s was %s', job_id, status.value)

def delete_containers(
        number_of_containers: int,
        container_image_name: str,
        job_id: str,
        message_dict: dict,
) -> None:
    '''
    The function deletes the specified number of container(s)
    based on the provided job details.
        Parameters:
            number_of_containers (int): Number of containers to delete
            container_image_name (str): Name of the container image to delete (more informative)
            job_id (str): Unique job identifier
            message_dict (dict): Dictionary containing job instruction
        Returns:
            None        
    '''
    # initialization of list, necessary to store container ID(s)
    containers_deleted = []

    # extract job ids
    container_ids = extract_container_ids(message_dict)

    for index, container_id in enumerate(container_ids, start=0):
        logger.info('Deleting container %s/%s with image %s',
                     index + 1, number_of_containers, container_image_name)
        try:
            container = docker_client.containers.get(container_id)
            container.kill()
            logger.info('Container %s/%s with Image %s has been successfully stopped, Container ID: %s',
                        index + 1, number_of_containers, container_image_name, container_id)

            containers_deleted.append(container_id)
            status = Status.SUCCESS

        except Exception as e:
            logger.info('Handling of Job Instruction for Job ID %s was not successful due to %s', job_id, e)
            status = Status.FAILURE
            # terminate for loop early
            break

    render_job_template_and_produce_job_status_message('delete', status, container_image_name, containers_deleted, job_id)

def message_handler(message_dict: dict) -> None:
    '''
    The function handles job instruction messages by performing 
    the specified operation.
        Parameters:
            message (dict): A dictionary representing the job instruction message.
        Returns:
            None
    '''
    # extract all relevant fields which are common, no matter the operation (create/delete)
    operation, number_of_containers, job_id, container_image_name = extract_message_values(message_dict)

    logger.info('Handle Job Instruction for Job ID %s - %s', job_id, operation)

    if operation == 'create':
        logger.info('Start Creation of %s %s Containers', number_of_containers, container_image_name)
        create_containers(number_of_containers, container_image_name, job_id, message_dict)

    elif operation == 'delete':
        # only handle messages which are relevant to handling agent, everything else not relevant
        if message_dict.get('metadata').get('agent_id') == agent_id:
            logger.info('Start Deletion of %s %s Containers', number_of_containers, container_image_name)
            delete_containers(number_of_containers, container_image_name, job_id, message_dict)
        else:
            logger.info('Deletion Job Instruction relevant to other Agent')

    # TODO - @leandro such messages should not arrive at my end because of schema validation right?
    else:
        logger.info('Unknown Job Instruction')

def consume_job_messages() -> None:
    '''
    The function consumes messages from the Kafka topic Job_Instruction and processes
    incoming message using the message_handler function (callback).
        Parameters:
            None
        Returns:
            None
    '''
    logger.info('Message Consumer for Topic Job_Instruction successfully called')
    topic_name = 'Job_Instruction'
    kafka_service.consume_messages(topic=[topic_name], message_handler=message_handler)

def observe_docker_daemon():
    ''''
    The function initializes the Docker client and checks if the connection
    to the Docker daemon is given.
        Parameters:
            None
        Returns:
            Status: Status.SUCCESS if the Docker client is functional,
                    Status.FAILURE otherwise
    '''
    global docker_client
    try:
        if docker_client is None:
            initialize_docker_client()
            # if initialization fails, DockerException is thrown
        if docker_client:
            # check, if info can be fetched to make sure, docker client has access to docker daemon
            # if fetch fails, Exception
            docker_client.info()

    except (DockerException, Exception):
        # return failure
        return Status.FAILURE

    else:
        # return success, if try block is executed properly
        return Status.SUCCESS

def observe_cpu_availability():
    '''
    The function observes the overall cpu availability
    by analyzing the cpu usage of all running containers.
        Parameters:
            None
        Returns:
            Status: Status.SUCCESS if total cpu usage is within acceptable limits,
                    Status.FAILURE otherwise (if total cpu usage exceeds 100%)
    '''
    try:
        overal_cpu_usage = 0
        for container_instance in docker_client.containers.list():
            container_statistics = container_instance.stats(decode=False, stream=False)

            # total cpu time (in nanoseconds) that the container has used since it started
            container_cpu_time_overall = container_statistics['cpu_stats']['cpu_usage']['total_usage']
            # total cpu time (in nanoseconds) that the container used during previous measurement period
            container_cpu_time_until_previous_period = container_statistics['precpu_stats']['cpu_usage']['total_usage']
            # delta represents cpu time (in nanoseconds) that the container used during the previous measurement period
            container_cpu_delta = container_cpu_time_overall - container_cpu_time_until_previous_period

            # total cpu time (in nanoseconds) that the whole system has used since it started
            system_cpu_time_overall = container_statistics['cpu_stats']['system_cpu_usage']
            # total cpu time (in nanoseconds) that the whole system used during previous measurement period
            system_cpu_time_until_previous_period = container_statistics['precpu_stats']['system_cpu_usage']
            # delta represents cpu time (in nanoseconds) that the whole system used during the previous measurement period
            system_cpu_delta = system_cpu_time_overall - system_cpu_time_until_previous_period

            # number of cpu cores available to the Docker daemon
            online_cpus = container_statistics['cpu_stats']['online_cpus']

            if system_cpu_delta > 0 and online_cpus > 0:
                cpu_percent = (container_cpu_delta / system_cpu_delta) * online_cpus * 100
            else:
                cpu_percent = 0

            overal_cpu_usage += cpu_percent
        if overal_cpu_usage > 100:
            # return failure, if no resources are available anymore
            return Status.FAILURE
        else:
            # return success, if still resources are available
            return Status.SUCCESS

    except Exception:
        # return failure
        return Status.FAILURE

# TODO - finalize
def observe_agent():
    while True:
        status, failed_checks = checker(docker_client=observe_docker_daemon(),
                         cpu_availability=observe_cpu_availability(),
                         check2=Status.SUCCESS,
                         check3=Status.SUCCESS)

        # print(docker_client.containers.list(filters={'label': 'sample_gen_orchestrator'}))
        if status == Status.FAILURE:
            print('agent hat zurzeit ein Problem')

        else:
            print('agent ist ready')

        render_heartbeat_template_and_produce_agent_status_message(status, failed_checks)
        logger.info('The Heartbeat was %s', status.value)

        sleep(check_interval)

def checker(**kwargs):
    '''
    The function checks the results of multiple status checks 
    and reports any failures.
    Parameters:
        **kwargs: Arbitrary keyword arguments where the key is the
                  name of the check and the value is the result of the check
    Returns:
        tuple: A tuple containing:
                - Status: Overall status, Status.FAILURE if any checks failed, otherwise Status.SUCCESS
                - failed_checks (list): A list of the names of failed checks 
    '''
    failed_checks = []

    for key, value in kwargs.items():
        if value == Status.FAILURE:
            failed_checks.append(key)
            print(f'The Check {key} failed')

    if failed_checks:
        print(f'The following Checks failed: {failed_checks}')
        return Status.FAILURE, failed_checks

    else:
        print('All Checks were performed successfully.')
        return Status.SUCCESS, failed_checks

def main():
    # TODO - block t2, if t1 is not successful
    t1 = threading.Thread(target=observe_agent)
    t2 = threading.Thread(target=consume_job_messages)

    t1.start()
    t2.start()

if __name__ == '__main__':
    main()
