import os
from dotenv import load_dotenv

class BaseConfig:
    def __init__(self) -> None:
        load_dotenv()
        self.load_environment_variables()

    def load_environment_variables(self) -> None:
        raise NotImplementedError("Subclasses should implement this method")

class KafkaConfig(BaseConfig):
    def load_environment_variables(self) -> None:
        self.bootstrap_servers_host: str = os.getenv('KAFKA_BOOTSTRAP_SERVERS_HOST', '')

        if not self.bootstrap_servers_host:
            raise ValueError("KAFKA_BOOTSTRAP_SERVERS_HOST environment variable not set")

class SchemaRegistryConfig(BaseConfig):
    def load_environment_variables(self) -> None:
        self.schema_registry_url = os.getenv('SCHEMA_REGISTRY_URL', '')

        if not self.schema_registry_url:
            raise ValueError("SCHEMA_REGISTRY_URL environment variable not set")

class DatabaseConfig(BaseConfig):
    def load_environment_variables(self) -> None:
        self.db_host: str = os.getenv('DB_HOST', '')
        self.db_user: str = os.getenv('DB_USER', '')
        self.db_password: str = os.getenv('DB_PASSWORD', '')

        if not self.db_host or not self.db_user or not self.db_password:
            raise ValueError("Database environment variables not set")
