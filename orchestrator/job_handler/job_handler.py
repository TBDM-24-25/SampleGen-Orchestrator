from orchestrator.services.kafka_service import KafkaService

# Mock data
data = {
    "topic": "temperature",
    # either create or delete, rerun = create
    "operation": "create",
    "container_image_name": "nginx",
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
    "computation_duration_in_seconds": 3600,
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
        "created_at": "2024-11-27T10:00:00Z",
        "requested_at": "2024-11-27T10:00:00Z",
        "run_at": "2024-11-27T10:00:00Z",
        "description": "This job generates temperature data for IoT simulation."
    }
}

def main():
    kafka_service = KafkaService(group_id='status_consumers')

    topic_name = 'Job_Handling'
    try:
        kafka_service.create_topic(topic_name)
    except ValueError as e:
        print(f"Topic already exists: {e}")
    except RuntimeError as e:
        print(f"Error creating topic: {e}")
        return

    try:
        kafka_service.send_message(topic_name, data)
    except RuntimeError as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    main()
