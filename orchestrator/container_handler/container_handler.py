import threading
from queue import Queue
from time import sleep, time
import logging

# TODO - check for proper import
# pylint: disable=import-error
# TODO check, what the issue with docker si
import docker

from orchestrator.services.kafka_service import KafkaService

# TODO - remove all print statements in the end

# initialize logger
logger = logging.getLogger('container_handler')
logging.basicConfig(filename='orchestrator/container_handler/logfile.log',
                    filemode='w',
                    encoding='utf-8',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# initialize KafkaService with group_id Job_Consumers
kafka_service = KafkaService(group_id='Job_Consumers')

# initialize docker client
docker_client = docker.client.from_env()

# TODO - should we persist the queue or can we live with it as is?
# initialize coordination queue for jobs, FIFO, thread-safe
job_queue = Queue()

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

    while True:
        if job_queue.empty():
            logger.info('Currently, there are no new Job Instructions to handle')

        # If job_queue consists of Elements, handle Job Instructions
        # TODO - handle create and delete job instruction
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

            created_at = time()

            # TODO - provide template
            data_container_operation = {
            "operation": "create",
            # TODO - how to handle errors?
            # if handled, successful / unsucessful possible
            "state": "successful",
            "container_image_name": container_image_name,
            "container_id": container_id,
            "metadata": {
                "job_id": job_id,
                # TODO - define ID of Handler, also necessary for
                "container_handler": "handler01",
                "timestamp": created_at,
                }
            }

            kafka_service.send_message('Job_Status', data_container_operation)

            # TODO - persist?
            handled_job_instructions.append({'job_id': job_id,
                                             'time_to_live': 60,
                                             'container_image_name': container_image_name,
                                             'container_id': container_id, 
                                             'timestamp': created_at})

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

                # TODO - provide template, gleiches wie oben!
                data_container_operation = {
                "operation": "stop",
                # successful / unsuccessful
                "state": "successful",
                "container_image_name": 'just a test',
                "container_id": 'just a test',
                "metadata": {
                    "job_id": 'just a test id',
                    "container_handler": "handler01",
                    "timestamp": time(),
                    }
                }

                kafka_service.send_message('Job_status', data_container_operation)
        # replace old list with updated list
        handled_job_instructions = filtered_list

        sleep(5)

# TODO - implement heartbeat agent
def observe_agent():
    pass

def main():
    # TODO checking if better way to manage threads
    t1 = threading.Thread(target=consume_job_messages)
    t2 = threading.Thread(target=handle_containers)
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()