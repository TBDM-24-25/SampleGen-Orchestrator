from services.kafka_service import KafkaService
from services.schema_service import SchemaService


# Mock data
data = {
    "data_type": "temperature",
    "topic": "temperature",
    "operation": "create",
    "container_image_name": "temperature-simulator",
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
    "ports": {
        "host_port": 8080,
        "container_port": 80
    },
    "environment_variables": [
        {"name": "PYTHON_VERSION", "value": "3.7"},
        {"name": "SPARK_VERSION", "value": "3.0.0"}
    ],
    "metadata": {
        "user": "user",
        "job_id": "job_id",
        "created_at": "2024-11-27T10:00:00Z",
        "requested_at": "2024-11-27T10:00:00Z",
        "run_at": "2024-11-27T10:00:00Z",
        "description": "This job generates temperature data for IoT simulation."
    }
}


def main():
    kafka_service = KafkaService()
    schema_service = SchemaService()
    schema = schema_service.create_schema(data=data)

    topic_name = 'my_topic5'
    try:
        kafka_service.create_topic(topic_name)
    except ValueError as e:
        print(f"Topic already exists: {e}")
    except RuntimeError as e:
        print(f"Error creating topic: {e}")
        return

    try:
        kafka_service.send_message(topic_name, schema)
    except RuntimeError as e:
        print(f"Error sending message: {e}")

    # Consume messages from the topic
    kafka_service.consume_messages([topic_name], group_id='my_group', process_message=process_message)

if __name__ == "__main__":
    main()