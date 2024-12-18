# Job Handler

This project implements a Kafka service and a schema service for managing topics, producing and consuming Kafka messages, and validating/rendering schemas using Jinja2 templates and Pydantic.

## Features

- **KafkaService**:
  - Create Kafka topics.
  - Produce messages to Kafka topics.
  - Consume messages from Kafka topics.

- **SchemaService**:
  - Validate schemas using Pydantic.
  - Render schemas using Jinja2 templates.


## Installation - Kafka
The application requires a Kafka cluster. For developers, Docker in combination with Docker Compose are recommended to deploy the cluster on the DEV machine. The project provides a corresponding Docker-Compose file to deploy all required Kafka instances.

1. Navigate to the root directory of the project
2. Run the following command in your shell:
```bash
docker compose -f kafka/docker-compose.yaml up -d
```
Be aware: Kafka might take a few seconds to be deployed

To stop the cluster, run the following Docker Compose command in your shell:
```bash
docker compose -f kafka/docker-compose.yaml down
```

## Installation - Orchestrator
1. Install Python version 3.13 or later
2. Create a virtual environment (within root folder):
```bash
python3.13 -m venv venv
```
3. Activate the virtual environment and make sure it has been activated correctly (which python3.13 should return the respective interpreter from the venv):
```bash
source venv/bin/activate
which python3.13
```
4. Install the dependencies:
```bash
python3.13 -m pip install -r requirements.txt
```
5. Open two different shells and set the environment variable in both:
```bash
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```
To check if the environment variable was set correctly, you can run: 
```bash
ENV | grep KAFKA_BOOTSTRAP_SERVERS
```
6. Make sure, your local docker daemon is running (exception handling not properly implemented yet)

7. Start the job handler (this will already trigger the first job, but as mentioned, exception handling is not implemented yet, finally, this is not an issue anymore):
```bash
python3.13 -m orchestrator.job_handler.job_handler
```
8. Start the container handler and check logfile if interested
```bash
python3.13 -m orchestrator.container_handler.container_handler
```

Whenever e new job is triggered with 7., the container handler processes the job instruction and starts up a dummy container, which runs for 1 minute locally


