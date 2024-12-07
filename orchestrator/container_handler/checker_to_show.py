
import docker
from docker.errors import DockerException

from time import sleep


docker_client = None

def initialize_docker_client():
    global docker_client
    try:
        docker_client = docker.client.from_env()    
    except DockerException:
        docker_client = None
        # reraise DockerException that agent observer can handle exception
        raise

def observe_agent():
    global docker_client

    while True:
        try:
            if docker_client is None:
                initialize_docker_client()
                # if initialization fails, DockerException, meaning docker Daemon not available
                print('initialized')

            if docker_client:
                # check, if info can be fetched to make sure, docker client still has access to docker daemon
                # if fetch fails, DockerException
                docker_client.info()
                print('alive')

        except DockerException:
            print('Client cannot be initialized')
        
        except Exception:
            print('Connection to Docker Daemon lost')


            # kafka_service.send_message('Agent_Status', 'test')
        
        sleep(2)

if __name__ == '__main__':
    observe_agent()