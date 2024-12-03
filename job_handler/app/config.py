from dotenv import load_dotenv
import os

class BaseConfig:
    def __init__(self) -> None:
        load_dotenv()
        self.load_environment_variables()

    def load_environment_variables(self) -> None:
        raise NotImplementedError("Subclasses should implement this method")

class KafkaConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.bootstrap_servers: str = ''
        self.topic_name_job_request: str = ''

    def load_environment_variables(self) -> None:
        self.bootstrap_servers: str = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '')
        self.topic_name_job_request: str = os.getenv('KAFKA_TOPIC_NAME_JOB_REQUEST', '')

        if not self.bootstrap_servers or not self.topic_name_job_request:
            raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable not set")

class SchemaRegistryConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.schema_registry_url: str = ''

    def load_environment_variables(self) -> None:
        self.schema_registry_url: str = os.getenv('SCHEMA_REGISTRY_URL', '')

        if not self.schema_registry_url:
            raise ValueError("SCHEMA_REGISTRY_URL environment variable not set")

class DatabaseConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.db_password: str = ''
        self.db_user: str = ''
        self.db_host: str = ''

    def load_environment_variables(self) -> None:
        self.db_host: str = os.getenv('DB_HOST', '')
        self.db_user: str = os.getenv('DB_USER', '')
        self.db_password: str = os.getenv('DB_PASSWORD', '')

        if not self.db_host or not self.db_user or not self.db_password:
            raise ValueError("Database environment variables not set")