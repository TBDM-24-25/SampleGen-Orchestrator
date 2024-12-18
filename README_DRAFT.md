# Distributed Data Generation (A Distributed Computation Framework Based on Kafka and Docker)

## 1) Project Description and Provided Features
The goal of this project is to provide a distributed computation framework to generate sample data, using Kafka and Docker. 

Via a Graphical User Interface, the user is able to submit jobs, providing only a small set of parameters (hidden logic). It are these jobs, which the framework takes care off, to fulfil the requirements provided by the user.

## 2) Framework Architecture
### 2.1) Architecture & Components

Angeben, dass wir schema registry verwenden


gemäss ihm 1 replication, 1 partition okay

frage an ihn: 
- 1 partition für unser fall, und wir nehmen zookeper image
- und 1 broker
- replication factorm = 1 
- wir brauchen image ohne zookeper, with kraft und so 
seine antwort: 1, 1,1 passt schon für uns
kraft passt auch für uns, aber dann gehen connectors eher nict. 

erwähnen dass wir 1,1 haben, und die limitationen aufzeigen






erwähnen, dass wir KRaft version von Kafka Verwenden




   ```bash
    export SCHEMA_REGISTRY_URL=http://localhost:8081
    ```

erwähnen dass eine limitation ist, dass wir nur von dockerhub ziehen


The proposed framework consists of five main components, which are described briefly subsequently:

1) **Job Handler**: @Leandro
2) **Kafka**: Distributed event streaming platform used to a) coordinate actions performed by the Job Handler and Container Handler, to b) provide agent observation mechanisms, and to c) offer an event streaming endpoint for the data generator(s). Whereas the topics for a) and b) are predefined and use schema validation, the topic for c) can be defined individually for every job submitted and does not validate messages.
3) **Container Handler**: @Christian
4) **Docker Daemon**: Service, responsible for orchestrating container lifecycle management. Thus, handling tasks such as container creation, execution, deletion and monitoring which are necessary to fulfil the jobs submitted.
5) **Data Generator(s)**: Docker containers, generating and providing sample data by publishing them towards a chosen/defined Kafka topic. The implementation of the Data Generator(s) is out-of-scope.

The graphical representation of the framework architecture and the interactions between the five different components can be found in the Figure 01 below:
![image](docs/images/architecture_overview.png)
*Figure 01: Architecture Overview*


As the Job Handler and the Container Handler (Agent) take on a crucial role within the framework, the will be described more detailed susequently.

### 2.2) Job Handler



### 2.3) Container Handler

![image](docs/images/container_handler.png)
*Figure 02: Architecture Overview Container Handler (Agent)*


### 2.4) Technologies used

To implement the distributed computation framework, the following technology stack was used:

![Apache Kafka](https://img.shields.io/badge/apache%20kafka-%23231F20.svg?style=for-the-badge&logo=apache-kafka&logoColor=white)![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)![JavaScript](https://img.shields.io/badge/javascript-%23F7DF1E.svg?style=for-the-badge&logo=javascript&logoColor=black)![Jinja](https://img.shields.io/badge/jinja-%23B41717.svg?style=for-the-badge&logo=jinja&logoColor=white)![Python](https://img.shields.io/badge/python-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white)






## 3) Getting Started
### 3.1) Prerequisites
- Python (V3.13)
- Docker daemon on all host machines to run agents on
- Furthermore, it is highly recommended to work within a Python virtual environment (venv) and install all dependencies within the venv. To do so, proceed as follows:
    1. Navigate to the root directory
    2. Create the Python virtual environment named venv:
        ```bash
        python3.13 -m venv venv
        ```
    3. Activate the virtual environment and make sure it has been activated correctly (which python3.13 should return the respective interpreter from the venv):
        ```bash
        source venv/bin/activate
        which python3.13 && which pip3.13
        # Ensure, the following ouput is returned:
        # ./venv/bin/python3.13
        # ./venv/bin/pip3.13
        ```
    4. Install the required dependencies:
        ```bash
        python3.13 -m pip install -r requirements.txt
        ```

### 3.2) Kafka
With the provided Docker compose file, the installation of Kafka is straightforward. Proceed as follows:
1. Navigate to the root directory
2. Start Kafka, the Graphical User Interface and the Schema registry by running the following command in your terminal:
   ```bash
    docker compose -f kafka/docker-compose.yaml up -d
    # be aware: Kafka might take a few seconds to be deployed

    # if it should be necessary to stop the cluster, use docker compose -f kafka/docker-compose.yaml down
    ```
3. (Optional) When Kafka has started up, you can access:<br>
    3.1 Kafka Grapical User Interface: http://localhost:8080<br>
    3.2 Schema registry: http://localhost:8081

### 3.2) Container Handler (Agent)
With the provided Docker compose file, the installation of Kafka is straightforward. Proceed as follows:
1. Navigate to the root directory
2. Set the following environment variable and check if it was set correctly by running the following command in your terminal:
    ```bash
    export KAFKA_BOOTSTRAP_SERVERS=localhost:9092

    ENV | grep KAFKA_BOOTSTRAP_SERVERS
    # Ensure, the following output is returned:
    # KAFKA_BOOTSTRAP_SERVERS=localhost:9092
    ```
3. Start the container handler. The respective log file can be found under ./orchestrator/container_handler/logfile.log:
    ```bash
    python3.13 -m orchestrator.container_handler.container_handler
    ```


### 3.2) Job Handler
todo


### usage

getting started
prerequisited
run locally, usage, further improvements 
-> aufteilen in kafka, frontend und generator, agents


## 4) Outlook
- hier sagen dass man alles noch paketieren könnte, vor allem agent und so, damit man alles schöner laufen lassen kann und auch nutzen kann
- evtl noch differenzierteres exception handling, etc. 

- sagen, dass man den agent containerisieren muss, auch wegen dependencies, etc. 

architecture

## 5) licensing

## 6) contacts
- **Christian Bieri**, Site Reliability Engineer, info@christianbieri.ch
- **Frederico Fischer**, Position, e-mail
- **Leandro Hoehnen**, Position, e-mail