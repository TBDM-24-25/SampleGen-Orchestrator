
from jinja2 import Environment, FileSystemLoader


# Mock data
data = {
    "data_type": "temperature",
    "topic": "temperature",
    "container_image_name": "temperature-simulator",
    "container_registry": {
        "url": "gcr.io/my-project/temperature-simulator:latest",
        "type": "private",
        "user_credentials": {
            "username": "username",
            "password": "password",
            "token": "token"
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

# Render the template
def render_template(data):
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("schema.yaml")

    filename = "test_schema.yaml"
    content = template.render(
        data
    )
    with open(filename, mode="w", encoding="utf-8") as test_schema:
        test_schema.write(content)
        print(f"... wrote {filename}")


def main():
    render_template(data)

if __name__ == "__main__":
    main()
