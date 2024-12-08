import threading
from queue import Queue
from time import sleep, time
import logging
from getmac import get_mac_address

import json

from jinja2 import Environment, FileSystemLoader

import docker
from docker.errors import DockerException


from orchestrator.services.kafka_service import KafkaService
from orchestrator.services.logger_service import GlobalLogger

# TODO - remove all print statements in the end

# initialize logger
logger = GlobalLogger(filename='orchestrator/container_handler/logfile.log').get_logger()

# initialize KafkaService with group_id Job_Consumers
kafka_service = KafkaService(group_id='Job_Consumers')

# TODO - should we persist the queue or can we live with it as is?
# initialize coordination queue for jobs, FIFO, thread-safe
job_queue = Queue()

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
    '''
    The function handles incoming messages for the topic Job_Handling
    by placing the message in the job_queue for further processing.
        Parameters:
            message (dict): A dictionary representing the job instruction message.
        Returns:
            None
    '''
    job_id = message.get('metadata').get('job_id')
    container_image_name = message.get('container_image_name')
    logger.info('A new Job Instruction has arrived: Job ID: %s, Image: %s', job_id, container_image_name)
    job_queue.put(message)
    logger.info('The Job Instruction for Job ID %s has been put into the Job queue', job_id)

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

def handle_containers():
    # initializing list to manage (keeping track of) handled job instructions
    handled_job_instructions = []

    job_template = environment.get_template('container_handler/job_status.json.j2')

    while True:
        if job_queue.empty():
            logger.info('Currently, there are no new Job Instructions to handle')

        # If job_queue consists of Elements, handle Job Instructions
        # TODO - handle create and delete job instruction define with @leandro
        else:
            # fetch latest element from job_queue
            job_instruction = job_queue.get()

            # TODO - provide function to extract job_id and container_image_name, because used in different parts
            job_id = job_instruction.get('metadata').get('job_id')
            container_image_name = job_instruction.get('container_image_name')
            
            logger.info('Handle Job Instruction for Job ID %s', job_id)
            # TODO - extract further details from @leandros message to start up containers
            container = docker_client.containers.run(container_image_name, detach=True)
            container_id = container.attrs.get('Id')
            logger.info('Job Instruction for Job ID %s successfully handled, container created with ID: %s', job_id, container_id)

            rendered_content = job_template.render(
                operation='create',
                state='successful',
                container_image_name=container_image_name,
                container_id=container_id,
                job_id=job_id
            )
            content = json.loads(rendered_content)

            ## hier gerendertes zeugs rein
            # job-status noch gluabal setzen weil an mehreren orten gebraucht wird
            kafka_service.send_message('Job_Status', content)

            # TODO - persist?
            handled_job_instructions.append({'job_id': job_id,
                                             'time_to_live': 60,
                                             'container_image_name': container_image_name,
                                             'container_id': container_id, 
                                             # TODO - das hier ist leicht anders als das was ich im rendering mache
                                             # problemantisch? ignorieren?
                                             'timestamp': time()})

        # initializing list to filter jobs which should still be tracked
        filtered_list = []
        logger.info('Currently, the following Job Instructions are being handled: %s', handled_job_instructions)
        for handled_job_instruction in handled_job_instructions:
            # TODO - allow dynamic behaviour, time to live
            # handling jobs which still should be alive
            if time() - handled_job_instruction.get('timestamp') < handled_job_instruction.get('time_to_live'):
                # as removing objects from a list is not save, appending still trackable job instructions in new list
                filtered_list.append(handled_job_instruction)
            # handling jobs which should no longer be alive
            else:
                container = docker_client.containers.get(handled_job_instruction.get('container_id'))
                container.kill()

                rendered_content = job_template.render(
                    operation='delete',
                    state='successful',
                    container_image_name=container_image_name,
                    container_id=container_id,
                    job_id=job_id
                )

                content = json.loads(rendered_content)


                kafka_service.send_message('Job_Status', content)

        # replace old list with updated list
        handled_job_instructions = filtered_list

        sleep(5)

# TODO - implement heartbeat agent
# TODO - Kafka integrieren??
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
                print(rendered_content)
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

def main():
    # TODO checking if better way to manage threads
    t1 = threading.Thread(target=consume_job_messages)
    t2 = threading.Thread(target=handle_containers)
    t3 = threading.Thread(target=observe_agent)

    t3.start()

    t1.start()
    t2.start()

    # try except finally hier?

    # irgendwie sicherstellen dann beim abschalten ein done kommt, und dass t3 quasi als erstes laufen muss
    # udn dann alles andere, preflight check!

    # wenn es ein problem gibt einfach nicht mehr konsumieren?? das könnte man auch machen, etc. 
    # lenadro reporten, wie viele container hier laufen? 
    # wie viel noch laufen kann? etc. etc. etc. 


if __name__ == '__main__':
    main()





