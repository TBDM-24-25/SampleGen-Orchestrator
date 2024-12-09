import threading
from time import sleep, time
import json
from getmac import get_mac_address
from jinja2 import Environment, FileSystemLoader

import docker
from docker.errors import DockerException

from orchestrator.services.kafka_service import KafkaService
from orchestrator.services.logger_service import GlobalLogger

# TODO - remove all print statements in the end
# TODO - set kafka publish topic globally?


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

def message_handler(message: dict) -> None:
    # TODO - to be defined
    '''
    # TODO
        Parameters:
            message (dict): A dictionary representing the job instruction message.
        Returns:
            None
    '''

    # load job_template
    job_template = environment.get_template('container_handler/job_status.json.j2')

    # TODO - provide a function to extract all values
    operation = message.get('operation')
    number_of_containers = message.get('number_of_containers')
    job_id = message.get('metadata').get('job_id')
    container_image_name = message.get('container_image_name')
    logger.info('Handle Job Instruction for Job ID %s - %s', job_id, operation)

    # TODO - check if enough resources are available to handle instructed job
    if operation == 'create':
        logger.info('Start Creation of %s %s Containers', number_of_containers, container_image_name)

        # initialization of list, necessary to store container ID(s)
        containers_created = []

        for index in range(number_of_containers):
            logger.info('Start creating Container with Index %s', index+1)
            try:
                # TODO - extract further details from @leandros message to start up containers
                container = docker_client.containers.run(container_image_name, detach=True)
                container_id = container.attrs.get('Id')

                logger.info('Container with Index %s has been successfully created, Container ID: %s', index+1, container_id)
                containers_created.append(container_id)

            except Exception as e:
                rendered_content = job_template.render(
                operation='create',
                state='unsuccessful',
                container_image_name=container_image_name,
                container_id=None,
                job_id=job_id)
                content = json.loads(rendered_content)

                kafka_service.send_message('Job_Status', content)
                logger.info('Handling of Job Instruction for Job ID %s was not successful due to %s', job_id, e)
                # terminate for loop early
                break
            else:
            # execute if no exception
                rendered_content = job_template.render(
                operation='create',
                state='successful',
                container_image_name=container_image_name,
                container_id=containers_created,
                job_id=job_id)
                content = json.loads(rendered_content)

                kafka_service.send_message('Job_Status', content)
                logger.info('Handling of Job Instruction for Job ID %s was successful', job_id)

    
    elif operation == 'delete':
        print('Something to delete!')
        # check, if agent ID relates to mine, if so, handle job, and commit, otherwise, do not care, do not commit
        # adjust kafka service to not perform commit after message handler has been called
#                 container = docker_client.containers.get(handled_job_instruction.get('container_id'))
#                 container.kill()

#                 rendered_content = job_template.render(
#                     operation='delete',
#                     state='successful',
#                     container_image_name=container_image_name,
#                     container_id=container_id,
#                     job_id=job_id
#                 )

#                 content = json.loads(rendered_content)


#                 kafka_service.send_message('Job_Status', content)
    
    else:
        print('I do not understand your job instruction!')

def consume_job_messages() -> None:
    '''
    The function consumes messages from the Kafka topic Job_Handling and processes
    incoming message using the message_handler function (callback).
        Parameters:
            None
        Returns:
            None
    '''
    logger.info('Message Consumer for Topic Job_Handling successfully called')
    topic_name = 'Job_Handling'
    kafka_service.consume_messages(topic=[topic_name], message_handler=message_handler)

# TODO - Finalize heartbeat agent, docker daemon check and resource check
# TODO - report number of containers, status of containers, resources
def observe_agent():
    global docker_client
    heartbeat_template = environment.get_template("container_handler/heartbeat.json.j2")
    while True:
        try:
            if docker_client is None:
                initialize_docker_client()
                # if initialization fails, DockerException is thrown
            if docker_client:
                # check, if info can be fetched to make sure, docker client has access to docker daemon
                # if fetch fails, Exception
                docker_client.info()

                # return successful heartbeat
                rendered_content = heartbeat_template.render(
                    state="successful"
                )
                # print(rendered_content)
                # parse JSON string, returned by render()
                content = json.loads(rendered_content)

                kafka_service.send_message('Agent_Status', content)

        except (DockerException, Exception):
            # return unsuccessful heartbeat
            rendered_content = heartbeat_template.render(
                state="unsuccessful"
            )
            # parse JSON string, returned by render()
            content = json.loads(rendered_content)

            kafka_service.send_message('Agent_Status', content)
    
        # perform healthcheck every 2 seconds
        # TODO - can also be another interval
        sleep(10)

def checker(**kwargs):
    pass

def main():
    # TODO checking if better way to manage threads

    t1 = threading.Thread(target=observe_agent)
    t2 = threading.Thread(target=consume_job_messages)

    t1.start()
    t2.start()

    # send done to leandro when finishing
    # make sure, t2 is blocked if t1 reports an error

if __name__ == '__main__':
    main()
