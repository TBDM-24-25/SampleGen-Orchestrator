from models import UserCredentials, ContainerRegistry, ResourceLimits, RetryPolicy, Ports, EnvironmentVariable, Metadata, Job
from services.kafka_service import KafkaService


# Mock data
# Create the object with the provided test data
user_credentials = UserCredentials(username="username", password="password", token=None)
container_registry = ContainerRegistry(url="gcr.io/my-project/temperature-simulator:latest", type="private", user_credentials=user_credentials)
resource_limits = ResourceLimits(cpu=1.0, memory="1Gi")
retry_policy = RetryPolicy(retry_on_failure=True, number_of_retries=3, backoff_period_in_ms=10)
ports = Ports(host_port=8080, container_port=80)
environment_variables = [EnvironmentVariable(name="PYTHON_VERSION", value="3.7"), EnvironmentVariable(name="SPARK_VERSION", value="3.0.0")]
metadata = Metadata(user="user", job_id="job_id", created_at="2024-11-27T10:00:00Z", requested_at="2024-11-27T10:00:00Z", run_at="2024-11-27T10:00:00Z", description="This job generates temperature data for IoT simulation.")


job_data = Job(
    data_type="temperature",
    topic="temperature",
    operation="create",
    container_image_name="temperature-simulator",
    container_registry=container_registry,
    computation_duration_in_seconds=3600,
    resource_limits=resource_limits,
    retry_policy=retry_policy,
    ports=ports,
    environment_variables=environment_variables,
    metadata=metadata
)


def process_message(msg: Job):
    print(f"Received message: {msg}")


def main():
    kafka_service = KafkaService()

    try:
        kafka_service.send_job(job_data)
    except RuntimeError as e:
        print(f"Error sending message: {e}")

    # Consume messages from the topic
    kafka_service.consume_messages(group_id='my_group', process_message=process_message)

if __name__ == "__main__":
    main()