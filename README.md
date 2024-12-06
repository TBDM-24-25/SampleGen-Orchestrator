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

## Installation
1. Install Python version 3.13 or later
2. Set the following enviroment variables:
  ```bash
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```
2.1 to be sure that the environemnt variable was set, check with
  ```bash
ENV | grep KAFKA_BOOTSTRAP_SERVERS
```

3. Install the dependencies
```bash
pip install -r requirements.txt
```
pip install . um alles zu builden

## Kafka Cluster
The application requires a Kafka cluster. For developers, Docker in combination with Docker Compose are recommended to deploy the cluster on the DEV machine. The project provides a corresponding Docker-Compose file to deploy all required Kafka instances.
### Kafka Deployment Instructions with Docker Compose
1. Go to the root directory of the project.
2. Run the following command in your shell:
```bash
docker compose -f kafka/docker-compose.yaml up -d
```

The cluster might take a few seconds to be deployed.

To stop the cluster, run the following Docker Compose command in your shell:
```bash
docker compose -f kafka/docker-compose.yaml down
```


aufstarten aus root mit 
python3.13 -m orchestrator.container_handler.container_handler

python3.13 -m orchestrator.job_handler.job_handler