from orchestrator.services.kafka_service import KafkaService

# Mock data
job_creation_data = {
    "operation": "create",
    "topic": "temperature",
    "container_image_name": "nginx",
    "number_of_containers": 2,
    # TODO - @leandro, @frederico, @christian, how far should we go when it comes to registry handling?
    "container_registry": {
        "url": "gcr.io/my-project/temperature-simulator:latest",
        "type": "private",
        "user_credentials": {
            "username": "username",
            "password": "password",
            "token": None
        }
    },
    "resource_limits": {
        "cpu": 1.0,
        # memory limits, string, with unit identifier such as b, k, m, g
        "memory": "1g"
    },
    "environment_variables": {
        "PYTHON_VERSION": "3.7",
        "SPARK_VERSION": "3.0.0"
    },
    "metadata": {
        "user": "user",
        "job_id": "job0001",
        # TODO - @ leandro, should we work with the posix timestamp here?
        "timestamp": "2024-11-27T10:00:00Z",
        "description": "This job generates temperature data for IoT simulation.",
        "computation_duration_in_seconds": 3600
    }
}

job_deletion_data = {
    "operation": "delete",
    "container_image_name": "nginx",
    "number_of_containers": 2,
    "metadata": {
        "job_id": "job0001",
        # TODO - @leandro, should we work with the posix timestamp here?
        "timestamp": "2024-11-27T10:00:00Z",
        "container_id": ["737e86cf56f54eb8e8f455c2838b0e92868a7a00cb69bc6f37150e4a1837d5c7", "b182fb4c1aade0beedb726f0a34e42d0b364ff4ae55d822e0faedff89d90209b"],
        "agent_id": "88:4d:7c:dc:93:0f"
    }
}


def main():
    kafka_service = KafkaService(group_id='job_status_consumers')

    topic_name = 'Job_Instruction'

    try:
        kafka_service.send_message(topic_name, job_creation_data)
    except RuntimeError as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    main()
