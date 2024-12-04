from confluent_kafka.schema_registry import SchemaRegistryClient, Schema, RegisteredSchema

from config import SchemaRegistryConfig

class SchemaRegistryService:
    __schema_subject_job_config = "job-request-value"
    __schema_registry_client: SchemaRegistryClient
    __schema_registry_config: dict

    def __init__(self):
        schema_registry_config = SchemaRegistryConfig()
        self.__schema_registry_config = {
            'url': schema_registry_config.schema_registry_url
        }
        self.__schema_registry_client = SchemaRegistryClient(self.__schema_registry_config)
        self.__register_schema()

    def __register_schema(self):
        with open(f"../../schema_registry/job_config.avsc") as f:
            schema_str = f.read()

        schema = Schema(schema_str, 'AVRO')
        schema_id = self.__schema_registry_client.register_schema(subject_name=self.__schema_subject_job_config, schema=schema)
        print(f"Registered schema with id: {schema_id}")

    def get_schema_and_registry_client(self) -> (RegisteredSchema, SchemaRegistryClient):
        latest_schema_version = self.__schema_registry_client.get_latest_version(self.__schema_subject_job_config)
        return latest_schema_version.schema, self.__schema_registry_client