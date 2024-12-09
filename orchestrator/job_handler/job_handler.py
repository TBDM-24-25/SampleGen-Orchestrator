from orchestrator.services.kafka_service import KafkaService

# Mock data
job_creation_data = {
    "operation": "delete",
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
        "memory": "1Gi"
    },
    "retry_policy": {
        "retry_on_failure": True,
        "number_of_retries": 3,
        "backoff_period_in_ms": 10
    },
    "environment_variables": [
        {"name": "PYTHON_VERSION", "value": "3.7"},
        {"name": "SPARK_VERSION", "value": "3.0.0"}
    ],
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
    "metadata": {
        # TODO - @leandro, should we work with the posix timestamp here?
        "timestamp": "2024-11-27T10:00:00Z",
        "container_id": "10e7f47e46eb57e1062509f6eff8b3e81f602edf3cf1f161438f533ef5a408d2",
        "agent_id": "88:4d:7c:dc:93:0f"
    }
}


def main():
    kafka_service = KafkaService(group_id='job_status_consumers')

    topic_name = 'Job_Handling'

    try:
        kafka_service.send_message(topic_name, job_creation_data)
    except RuntimeError as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    main()
